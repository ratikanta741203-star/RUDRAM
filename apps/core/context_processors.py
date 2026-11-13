from django.conf import settings
from apps.core.models import DataSourceStatus, get_global_demo_mode

PAGE_LABELS = {
    'dashboard': 'Disaster intelligence dashboard',
    'map': 'Multi-hazard risk map',
    'disasters_list': 'Disaster monitor',
    'disaster_detail': 'Incident details',
    'risk_prediction': 'Flood risk assessment',
    'population': 'Population exposure',
    'drone_view': 'Drone monitoring',
    'alerts': 'Emergency alerts',
    'evacuation': 'Evacuation planning',
    'shelters': 'Emergency shelters',
    'resources': 'Emergency resources',
    'resource_dispatch': 'Resource dispatch',
    'resource_update_stock': 'Update resource stock',
    'team_status_update': 'Rescue team status',
    'assistant': 'Emergency assistant',
    'satellite': 'Satellite analysis',
    'reports': 'Situation reports',
    'settings': 'System settings',
    'admin_dashboard': 'Admin command center',
    'operator_dashboard': 'Operator control room',
    'login': 'Sign in',
    'citizen_signup': 'Create a citizen account',
}

def rudram_context(request):
    data_sources = DataSourceStatus.objects.all()
    active_alerts_count = 0
    try:
        from apps.alerts.models import Alert
        active_alerts_count = Alert.objects.filter(is_active=True).count()
    except Exception:
        pass

    user_role = 'CITIZEN'
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role:
            user_role = request.user.profile.role
        elif request.user.is_superuser:
            user_role = 'ADMIN'

    demo_mode = get_global_demo_mode()
    data_source_label = 'RUDRAM Central Demo Dataset' if demo_mode else 'Live Sensor & API Telemetry'

    return {
        'DEMO_MODE': demo_mode,
        'DATA_SOURCE_LABEL': data_source_label,
        'DATA_SOURCES': data_sources,
        'ACTIVE_ALERTS_COUNT': active_alerts_count,
        'USER_ROLE': user_role,
        'APP_NAME': 'RUDRAM',
        'APP_TAGLINE': 'Predict. Protect. Respond. Recover.',
        'CARTO_BASEMAP_API_KEY': getattr(settings, 'CARTO_BASEMAP_API_KEY', ''),
        'SITE_URL': settings.SITE_URL,
        'PUBLIC_ORGANIZATION_EMAIL': settings.PUBLIC_ORGANIZATION_EMAIL,
        'PUBLIC_ORGANIZATION_PHONE': settings.PUBLIC_ORGANIZATION_PHONE,
        'SEO_PAGE_TITLE': PAGE_LABELS.get(
            getattr(getattr(request, 'resolver_match', None), 'url_name', None),
            'Disaster intelligence',
        ),
    }
