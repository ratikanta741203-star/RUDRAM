from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.risk.models import RiskPrediction, RiskZone
from apps.risk.serializers import RiskPredictionSerializer, RiskZoneSerializer
from ml.risk_prediction.model import risk_predictor
from apps.core.models import AuditLog

def risk_prediction_view(request):
    latest_predictions = RiskPrediction.objects.all()[:10]
    zones = RiskZone.objects.filter(is_active=True)
    context = {
        'latest_predictions': latest_predictions,
        'zones': zones,
        'page_title': 'AI Flood Risk Prediction Engine'
    }
    return render(request, 'risk/predict.html', context)

class RiskPredictAPIView(APIView):
    """
    POST /api/risk/predict/
    Accepts environmental & hydrological parameters (or lat/lon) and runs XGBoost/RandomForest flood prediction.
    Automatically fetches live Open-Meteo weather & 7-day forecast telemetry when lat/lon is provided.
    """
    def post(self, request):
        data = request.data.copy()
        lat = float(data.get('latitude', 20.2961))
        lon = float(data.get('longitude', 85.8245))
        loc_name = data.get('location_name', data.get('catchment_location', 'Selected Location'))

        weather_telemetry = {}
        forecast_7d = []

        # Automatically fetch live weather telemetry if environmental features are omitted
        try:
            from services.open_meteo import open_meteo_service
            from services.google_maps_service import google_maps_service

            curr_w = open_meteo_service.get_current_weather(lat, lon)
            fore_w = open_meteo_service.get_forecast(lat, lon, forecast_days=7)
            elevation = google_maps_service.get_elevation(lat, lon)

            if curr_w.get('success'):
                c_data = curr_w.get('current', {})
                weather_telemetry = {
                    'temperature_c': float(c_data.get('temperature', 28.0)),
                    'humidity_pct': float(c_data.get('humidity', 80.0)),
                    'wind_speed_kmh': float(c_data.get('wind_speed', 15.0)),
                    'rainfall_current_mm': float(c_data.get('rainfall', 0.0)),
                    'weather_code': c_data.get('weather_code', 0),
                    'condition': c_data.get('condition', 'Clear Sky'),
                    'elevation_m': float(elevation) if elevation is not None else 25.0
                }
                if 'rainfall_current_mm' not in data:
                    data['rainfall_current_mm'] = weather_telemetry['rainfall_current_mm']
                if 'temperature_c' not in data:
                    data['temperature_c'] = weather_telemetry['temperature_c']
                if 'humidity_pct' not in data:
                    data['humidity_pct'] = weather_telemetry['humidity_pct']
                if 'wind_speed_kmh' not in data:
                    data['wind_speed_kmh'] = weather_telemetry['wind_speed_kmh']
                if 'elevation_m' not in data:
                    data['elevation_m'] = weather_telemetry['elevation_m']

            if fore_w.get('success'):
                d_data = fore_w.get('daily', {})
                p_sums = d_data.get('precipitation_sum', [])
                p_times = d_data.get('time', [])
                t_max = d_data.get('temperature_max', [])
                t_min = d_data.get('temperature_min', [])

                for i in range(min(len(p_sums), 7)):
                    forecast_7d.append({
                        'date': p_times[i] if i < len(p_times) else f"Day {i+1}",
                        'rain_mm': float(p_sums[i]) if i < len(p_sums) else 0.0,
                        'temp_max': float(t_max[i]) if i < len(t_max) else 30.0,
                        'temp_min': float(t_min[i]) if i < len(t_min) else 22.0
                    })

                if p_sums:
                    if 'rainfall_forecast_24h_mm' not in data:
                        data['rainfall_forecast_24h_mm'] = float(p_sums[0])
                    if 'rainfall_24h_mm' not in data:
                        data['rainfall_24h_mm'] = float(p_sums[0])
                    if 'rainfall_7d_mm' not in data:
                        data['rainfall_7d_mm'] = float(sum(p_sums[:7]))

        except Exception as w_err:
            import logging
            logging.getLogger(__name__).warning(f"Error fetching live weather for risk prediction: {w_err}")

        # Run multi-disaster ML engine inference
        result = risk_predictor.predict_multi_disaster(data)

        # Save prediction record
        pred = RiskPrediction.objects.create(
            location_name=loc_name,
            latitude=lat,
            longitude=lon,
            rainfall_current_mm=float(data.get('rainfall_current_mm', 0.0)),
            rainfall_24h_mm=float(data.get('rainfall_24h_mm', 0.0)),
            rainfall_7d_mm=float(data.get('rainfall_7d_mm', 0.0)),
            rainfall_forecast_24h_mm=float(data.get('rainfall_forecast_24h_mm', 0.0)),
            temperature_c=float(data.get('temperature_c', 28.0)),
            humidity_pct=float(data.get('humidity_pct', 80.0)),
            wind_speed_kmh=float(data.get('wind_speed_kmh', 15.0)),
            elevation_m=float(data.get('elevation_m', 25.0)),
            slope_deg=float(data.get('slope_deg', 2.5)),
            distance_to_water_km=float(data.get('distance_to_water_km', 1.2)),
            river_water_level_m=float(data.get('river_water_level_m', 0.0)),
            risk_score=result['risk_percentage'],
            risk_level=result['risk_level'],
            confidence=result['confidence'],
            model_mode=result['model_mode'],
            is_demo=False,
            recommended_action=result['recommended_action'],
            contributing_factors=result['contributing_factors']
        )

        return Response({
            'success': True,
            'prediction': RiskPredictionSerializer(pred).data,
            'explanation': result,
            'risk_score': result['risk_percentage'],
            'risk_percentage': result['risk_percentage'],
            'risk_type': result['risk_type'],
            'risk_level': result['risk_level'],
            'flood_risk_pct': result['flood_risk_pct'],
            'cyclone_risk_pct': result['cyclone_risk_pct'],
            'cyclone': result.get('cyclone', {}),
            'weather_telemetry': weather_telemetry,
            'forecast_7d': forecast_7d,
            'river_level': None # River station data unavailable unless explicit station matched
        }, status=status.HTTP_200_OK)

ODISHA_DEFAULT_RISK_ZONES = [
    {
        "name": "Cuttack Mahanadi-Kathajodi Riverine Basin",
        "district": "Cuttack",
        "state": "Odisha",
        "risk_level": "CRITICAL",
        "risk_score": 88,
        "center_lat": 20.4625,
        "center_lon": 85.8828,
        "population_count": 18500,
        "vulnerable_buildings": 1420
    },
    {
        "name": "Puri Coastal Inundation & Lagoon Belt",
        "district": "Puri",
        "state": "Odisha",
        "risk_level": "HIGH",
        "risk_score": 78,
        "center_lat": 19.8135,
        "center_lon": 85.8312,
        "population_count": 14200,
        "vulnerable_buildings": 980
    },
    {
        "name": "Bhubaneswar Daya-Kuakhai Floodplain",
        "district": "Khordha",
        "state": "Odisha",
        "risk_level": "CRITICAL",
        "risk_score": 84,
        "center_lat": 20.2961,
        "center_lon": 85.8245,
        "population_count": 24000,
        "vulnerable_buildings": 1850
    },
    {
        "name": "Baleswar Subarnarekha Basin",
        "district": "Baleswar",
        "state": "Odisha",
        "risk_level": "HIGH",
        "risk_score": 76,
        "center_lat": 21.4934,
        "center_lon": 86.9135,
        "population_count": 16200,
        "vulnerable_buildings": 1100
    },
    {
        "name": "Kendrapara Deltaic Overflow Zone",
        "district": "Kendrapara",
        "state": "Odisha",
        "risk_level": "CRITICAL",
        "risk_score": 89,
        "center_lat": 20.5005,
        "center_lon": 86.4215,
        "population_count": 19800,
        "vulnerable_buildings": 1560
    },
    {
        "name": "Bhadrak Salandi Catchment Depression",
        "district": "Bhadrak",
        "state": "Odisha",
        "risk_level": "HIGH",
        "risk_score": 72,
        "center_lat": 21.0574,
        "center_lon": 86.4965,
        "population_count": 11500,
        "vulnerable_buildings": 840
    },
    {
        "name": "Ganjam Rushikulya Riverine Zone",
        "district": "Ganjam",
        "state": "Odisha",
        "risk_level": "MODERATE",
        "risk_score": 58,
        "center_lat": 19.3149,
        "center_lon": 84.7941,
        "population_count": 9200,
        "vulnerable_buildings": 610
    },
    {
        "name": "Sambalpur Hirakud Downstream Floodplain",
        "district": "Sambalpur",
        "state": "Odisha",
        "risk_level": "HIGH",
        "risk_score": 74,
        "center_lat": 21.4669,
        "center_lon": 83.9812,
        "population_count": 13800,
        "vulnerable_buildings": 920
    }
]

class RiskZoneListAPIView(APIView):
    def get(self, request):
        from apps.core.models import get_global_demo_mode
        is_demo = get_global_demo_mode()

        if is_demo:
            from demo.loader import get_demo_data_by_key
            demo_zones = get_demo_data_by_key('risk_zones', [])
            return Response({
                'success': True,
                'is_demo': True,
                'source': 'RUDRAM Demo Dataset',
                'count': len(demo_zones),
                'zones': demo_zones
            }, status=status.HTTP_200_OK)

        # Live Mode ONLY (No demo data fallback)
        zones = RiskZone.objects.filter(is_active=True)
        serializer = RiskZoneSerializer(zones, many=True)
        return Response({
            'success': True,
            'is_demo': False,
            'source': 'Live Telemetry & Sensors',
            'count': zones.count(),
            'zones': serializer.data
        }, status=status.HTTP_200_OK)

