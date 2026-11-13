from django.urls import path
from apps.core import views

urlpatterns = [
    path('robots.txt', views.robots_txt_view, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml_view, name='sitemap_xml'),
    path('llms.txt', views.llms_txt_view, name='llms_txt'),
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('map/', views.gis_map_view, name='map'),
    path('settings/', views.settings_view, name='settings'),
    path('api/health/', views.HealthCheckAPIView.as_view(), name='api_health'),
    path('api/data-sources/', views.DataSourcesAPIView.as_view(), name='api_data_sources'),
    path('api/data-sources/status/', views.DataSourcesAPIView.as_view(), name='api_data_sources_status_alias'),
    path('api/locations/states/', views.IndianStatesAPIView.as_view(), name='api_states'),
    path('api/locations/india-hubs/', views.IndiaHubsAPIView.as_view(), name='api_india_hubs'),
    path('api/locations/high-alerts/', views.HighAlertLocationsAPIView.as_view(), name='api_high_alerts'),
    path('api/admin/demo-mode/', views.AdminDemoModeAPIView.as_view(), name='api_admin_demo_mode'),
]
