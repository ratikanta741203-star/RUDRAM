from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, viewsets
from rest_framework.response import Response
from apps.disasters.models import Disaster, DisasterTimeline
from apps.disasters.serializers import DisasterSerializer, DisasterTimelineSerializer
from apps.shelters.models import Shelter
from apps.resources.models import RescueTeam, Resource
from apps.alerts.models import Alert
from apps.accounts.permissions import admin_required

@admin_required
def drone_view(request):
    """
    RUDRAM Live Drone Telemetry & Stream Monitoring Interface (Admin-Only).
    /drone-view/
    """
    context = {
        'page_title': 'Admin Live Drone Telemetry & Video Feed',
        'drone_stream_available': False,
        'stream_status_msg': 'DRONE STREAM OFFLINE — NO LIVE DRONE FEED AVAILABLE',
        'active_drones_count': 0,
    }
    return render(request, 'disasters/drone.html', context)

def disasters_list_view(request):
    # Live Multi-Disaster Analysis for 3 Main Cards (FLOOD, CYCLONE, EARTHQUAKE)
    flood_summary = {'available': False, 'risk_percentage': 0, 'high_risk_places': 0, 'total_monitored': 0}
    cyclone_summary = {'available': False, 'risk_percentage': 0, 'high_risk_places': 0, 'total_monitored': 0}
    earthquake_summary = {'available': False, 'risk_percentage': '--', 'high_risk_places': 'Data unavailable', 'status_msg': 'No live earthquake source configured'}

    try:
        from apps.core.locations import get_districts_for_state
        from services.open_meteo import open_meteo_service
        from ml.risk_prediction.model import risk_predictor
        from ml.risk_prediction.cyclone_model import cyclone_risk_predictor

        odisha_districts = get_districts_for_state('Odisha')
        district_weather = open_meteo_service.get_batch_weather(odisha_districts)

        valid_districts = [d for d in district_weather if d.get('is_available') is not False and d.get('temperature') is not None]

        if valid_districts:
            flood_risks = []
            cyclone_risks = []
            flood_locations = []
            cyclone_locations = []

            for d in valid_districts:
                dist_name = d.get('district', d.get('name', 'Unknown'))
                lat = float(d.get('lat', d.get('latitude', 20.2961)))
                lon = float(d.get('lon', d.get('longitude', 85.8245)))

                raw_feat = {
                    'latitude': lat,
                    'longitude': lon,
                    'rainfall_current_mm': d.get('rainfall', 0.0),
                    'rainfall_24h_mm': (d.get('rainfall', 0.0) or 0.0) * 5.0,
                    'temperature_c': d.get('temperature', 28.0),
                    'humidity_pct': d.get('humidity', 80.0),
                    'wind_speed_kmh': d.get('wind_speed', 15.0),
                    'weather_code': d.get('weather_code', 0)
                }

                f_res = risk_predictor.predict(raw_feat)
                c_res = cyclone_risk_predictor.predict(raw_feat)

                f_score = float(f_res.get('risk_score', 0.0))
                c_score = float(c_res.get('risk_percentage', 0.0))

                flood_risks.append(f_score)
                cyclone_risks.append(c_score)

                flood_locations.append({
                    'name': dist_name,
                    'district': dist_name,
                    'lat': lat,
                    'lon': lon,
                    'risk_pct': round(f_score, 1),
                    'risk_level': f_res.get('risk_level', 'LOW'),
                    'rainfall_24h_mm': (d.get('rainfall', 0.0) or 0.0) * 5.0,
                    'temp_c': d.get('temperature', 28.0)
                })

                cyclone_locations.append({
                    'name': dist_name,
                    'district': dist_name,
                    'lat': lat,
                    'lon': lon,
                    'risk_pct': round(c_score, 1),
                    'risk_level': c_res.get('risk_level', 'LOW'),
                    'wind_speed_kmh': d.get('wind_speed', 15.0),
                    'humidity_pct': d.get('humidity', 80.0)
                })

            flood_locations.sort(key=lambda x: x['risk_pct'], reverse=True)
            cyclone_locations.sort(key=lambda x: x['risk_pct'], reverse=True)

            f_high_count = sum(1 for s in flood_risks if s >= 50.0)
            c_high_count = sum(1 for s in cyclone_risks if s >= 50.0)

            flood_summary = {
                'available': True,
                'risk_percentage': round(max(flood_risks), 1) if flood_risks else 0.0,
                'high_risk_places': f_high_count,
                'total_monitored': len(valid_districts),
                'locations': flood_locations
            }

            cyclone_summary = {
                'available': True,
                'risk_percentage': round(max(cyclone_risks), 1) if cyclone_risks else 0.0,
                'high_risk_places': c_high_count,
                'total_monitored': len(valid_districts),
                'locations': cyclone_locations
            }

    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Live disaster summary calculation error: {e}")

    import json
    from apps.disasters.knowledge_data import DISASTER_KNOWLEDGE_DATA

    context = {
        'flood_summary': flood_summary,
        'cyclone_summary': cyclone_summary,
        'earthquake_summary': earthquake_summary,
        'flood_locations_json': json.dumps(flood_summary.get('locations', [])),
        'cyclone_locations_json': json.dumps(cyclone_summary.get('locations', [])),
        'knowledge_data': DISASTER_KNOWLEDGE_DATA,
        'knowledge_data_json': json.dumps(DISASTER_KNOWLEDGE_DATA),
        'active_count': Disaster.objects.filter(status='ACTIVE').count(),
        'critical_count': Disaster.objects.filter(severity='CRITICAL').count(),
        'page_title': 'Disaster Monitor'
    }
    return render(request, 'disasters/list.html', context)

def disaster_detail_view(request, pk):
    disaster = get_object_or_404(Disaster, pk=pk)
    timeline = disaster.timeline.all()
    nearby_shelters = Shelter.objects.filter(status='OPEN')[:5]
    rescue_teams = RescueTeam.objects.all()[:5]
    alerts = Alert.objects.filter(is_active=True)[:5]
    context = {
        'disaster': disaster,
        'timeline': timeline,
        'shelters': nearby_shelters,
        'rescue_teams': rescue_teams,
        'alerts': alerts,
        'page_title': f"{disaster.title} - Incident Room"
    }
    return render(request, 'disasters/detail.html', context)

from apps.accounts.permissions import IsAdminOrReadOnly

class DisasterViewSet(viewsets.ModelViewSet):
    queryset = Disaster.objects.all()
    serializer_class = DisasterSerializer
    permission_classes = [IsAdminOrReadOnly]
