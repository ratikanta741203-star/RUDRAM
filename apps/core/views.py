import os
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.utils.html import escape
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import DataSourceStatus, AuditLog
from apps.core.locations import INDIAN_STATES_DATA, ALL_INDIA_HUBS, HIGH_ALERT_LOCATIONS_DEFAULT
from apps.disasters.models import Disaster
from apps.shelters.models import Shelter
from apps.alerts.models import Alert
from apps.risk.models import RiskZone, RiskPrediction
from apps.resources.models import Resource, RescueTeam
from apps.population.models import PopulationExposure
from apps.infrastructure.models import River, Dam, Infrastructure

from django.views.decorators.csrf import ensure_csrf_cookie

def home_view(request):
    return redirect('dashboard')

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def robots_txt_view(request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /api/',
        'Disallow: /login/',
        'Disallow: /citizen/signup/',
        'Disallow: /admin-dashboard/',
        'Disallow: /operator-dashboard/',
    ]
    if settings.SITE_URL:
        lines.append(f'Sitemap: {settings.SITE_URL}/sitemap.xml')
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')

def llms_txt_view(request):
    content = """# RUDRAM 2.0

> Disaster intelligence and emergency response platform focused on risk monitoring, situational awareness, and response coordination.

RUDRAM provides tools for monitoring multi-hazard events, assessing flood risk, viewing geographic risk layers, coordinating shelters and resources, planning evacuations, and reviewing satellite analysis.

## Main sections
- [Dashboard](/dashboard/): disaster and weather overview.
- [Disaster monitor](/disasters/): active hazard information and response guidance.
- [Risk assessment](/risk/): location-based flood risk assessment.
- [GIS risk map](/map/): geographic hazard and response layers.
- [Emergency alerts](/alerts/): alert coordination.
- [Evacuation planning](/evacuation/): route planning to shelters.
- [Shelters](/shelters/): shelter availability and recommendations.
- [Resources](/resources/): relief resources and rescue teams.
- [Satellite analysis](/satellite/): satellite-based analysis tools.
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')

def sitemap_xml_view(request):
    if not settings.SITE_URL:
        return HttpResponseServerError(
            'Set SITE_URL to the public HTTPS origin before publishing the sitemap.',
            content_type='text/plain; charset=utf-8',
        )

    public_pages = (
        'dashboard', 'disasters_list', 'risk_prediction', 'map', 'alerts',
        'evacuation', 'shelters', 'resources', 'satellite',
    )
    locations = ''.join(
        f'<url><loc>{escape(settings.SITE_URL + reverse(page_name))}</loc></url>'
        for page_name in public_pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{locations}</urlset>'
    )
    return HttpResponse(xml, content_type='application/xml; charset=utf-8')

@ensure_csrf_cookie
def dashboard_view(request):
    """
    RUDRAM Location-Driven Weather & Disaster Operations Command Center.
    """
    disasters = Disaster.objects.all()
    active_disaster = disasters.filter(status='ACTIVE').first() or disasters.first()
    high_risk_zones = RiskZone.objects.filter(risk_level__in=['HIGH', 'CRITICAL'])
    shelters = Shelter.objects.all()
    available_shelters = shelters.filter(status__in=['OPEN', 'NEAR_CAPACITY'])
    active_alerts = Alert.objects.filter(is_active=True)
    pop_zones = PopulationExposure.objects.all()
    total_exposed = sum(p.exposed_population for p in pop_zones)
    rescue_teams = RescueTeam.objects.all()
    data_sources = DataSourceStatus.objects.all()
    rivers = River.objects.all()

    context = {
        'active_disaster': active_disaster,
        'disasters_count': disasters.filter(status='ACTIVE').count(),
        'high_risk_zones_count': high_risk_zones.count(),
        'total_exposed_population': total_exposed,
        'available_shelters_count': available_shelters.count(),
        'active_alerts_count': active_alerts.count(),
        'active_alerts': active_alerts[:5],
        'shelters': shelters[:5],
        'rescue_teams': rescue_teams[:5],
        'rivers': rivers[:4],
        'data_sources': data_sources,
        'indian_states': INDIAN_STATES_DATA,
        'high_alerts': HIGH_ALERT_LOCATIONS_DEFAULT,
        'page_title': 'RUDRAM Weather & Disaster Command Center'
    }
    return render(request, 'dashboard/index.html', context)

def gis_map_view(request):
    """
    Interactive Leaflet GIS Map with 21 togglable layers.
    """
    disasters = Disaster.objects.all()
    shelters = Shelter.objects.all()
    infra = Infrastructure.objects.all()
    rivers = River.objects.all()
    dams = Dam.objects.all()
    pop_zones = PopulationExposure.objects.all()

    shelters_data = [{
        'id': s.id,
        'name': s.name,
        'address': s.address,
        'latitude': float(s.latitude),
        'longitude': float(s.longitude),
        'available_capacity': s.available_capacity,
        'total_capacity': s.total_capacity,
        'elevation_m': float(s.elevation_m) if s.elevation_m else 0.0,
    } for s in shelters]

    context = {
        'disasters': disasters,
        'shelters': shelters,
        'shelters_json': shelters_data,
        'infrastructure': infra,
        'rivers': rivers,
        'dams': dams,
        'population_zones': pop_zones,
        'page_title': 'Interactive GIS Multi-Hazard Risk Map'
    }
    return render(request, 'map/index.html', context)

def settings_view(request):
    data_sources = DataSourceStatus.objects.all()
    audit_logs = AuditLog.objects.all()[:20]
    context = {
        'data_sources': data_sources,
        'audit_logs': audit_logs,
        'page_title': 'System Settings & Data Source Telemetry'
    }
    return render(request, 'settings/index.html', context)

class HealthCheckAPIView(APIView):
    """
    GET /api/health/
    Verifies Django, Database connectivity, DEMO_MODE, and External Services.
    """
    def get(self, request):
        db_connected = True
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                if not row or row[0] != 1:
                    db_connected = False
        except Exception:
            db_connected = False

        status_str = "healthy" if db_connected else "unhealthy"

        sources_stat = {}
        for s in DataSourceStatus.objects.all():
            sources_stat[s.source_name] = {
                'status': s.status,
                'is_live': s.is_live,
                'last_updated': s.last_updated
            }

        return Response({
            'status': status_str,
            'application': 'RUDRAM',
            'version': '1.0.0-hackathon-release',
            'tagline': 'Predict. Protect. Respond. Recover.',
            'database': 'connected' if db_connected else 'disconnected',
            'database_engine': settings.DATABASES['default']['ENGINE'],
            'demo_mode': settings.DEMO_MODE,
            'external_services': sources_stat
        })

class DataSourcesAPIView(APIView):
    """
    GET /api/data-sources/
    """
    def get(self, request):
        sources = DataSourceStatus.objects.all()
        data = [{
            'source_name': s.source_name,
            'display_name': s.display_name,
            'category': s.category,
            'status': s.status,
            'endpoint_url': s.endpoint_url,
            'is_live': s.is_live,
            'response_time_ms': s.response_time_ms,
            'last_updated': s.last_updated,
            'error_message': s.error_message
        } for s in sources]
        return Response({'success': True, 'sources': data})

class IndianStatesAPIView(APIView):
    """
    GET /api/locations/states/
    Returns all 28 States and 8 Union Territories with centroid coordinates.
    """
    def get(self, request):
        return Response({
            'success': True,
            'total': len(INDIAN_STATES_DATA),
            'states': INDIAN_STATES_DATA
        })

class IndiaHubsAPIView(APIView):
    """
    GET /api/locations/india-hubs/
    Returns major national meteorological and disaster monitoring hubs.
    """
    def get(self, request):
        return Response({
            'success': True,
            'total': len(ALL_INDIA_HUBS),
            'hubs': ALL_INDIA_HUBS
        })

class HighAlertLocationsAPIView(APIView):
    """
    GET /api/locations/high-alerts/
    Returns locations currently identified with high or critical disaster risk.
    """
    def get(self, request):
        return Response({
            'success': True,
            'total': len(HIGH_ALERT_LOCATIONS_DEFAULT),
            'alerts': HIGH_ALERT_LOCATIONS_DEFAULT
        })

class AdminDemoModeAPIView(APIView):
    """
    POST /api/admin/demo-mode/
    Toggles global DEMO_MODE setting. Requires ADMIN role or superuser.
    """
    def post(self, request):
        from apps.accounts.permissions import is_strict_admin
        if not is_strict_admin(request.user):
            return Response({'success': False, 'message': 'Access Denied. Only system administrators can change Demo Mode.'}, status=status.HTTP_403_FORBIDDEN)

        demo_val = request.data.get('demo_mode', False)
        is_demo = str(demo_val).lower() in ('true', '1', 't', 'yes')

        from apps.core.models import set_global_demo_mode, AuditLog
        set_global_demo_mode(is_demo)

        AuditLog.objects.create(
            user_name=request.user.username,
            action='UPDATE_DEMO_MODE',
            target_model='SystemSetting',
            details=f"Set Global DEMO_MODE to {'ON (Simulation)' if is_demo else 'OFF (Live Data)'}"
        )

        return Response({
            'success': True,
            'demo_mode': is_demo,
            'message': f"Global Demo Data Mode set to {'ON' if is_demo else 'OFF (LIVE DATA ONLY)'}."
        }, status=status.HTTP_200_OK)

