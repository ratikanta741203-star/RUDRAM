from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views

# Custom Admin Site Branding
admin.site.site_header = "RUDRAM Disaster Intelligence - Command Center"
admin.site.site_title = "RUDRAM Admin"
admin.site.index_title = "Disaster Resilience & Incident Operations Control"

urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    # RUDRAM Core & Feature Apps
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.disasters.urls')),
    path('', include('apps.risk.urls')),
    path('', include('apps.weather.urls')),
    path('', include('apps.population.urls')),
    path('', include('apps.infrastructure.urls')),
    path('', include('apps.shelters.urls')),
    path('', include('apps.resources.urls')),
    path('', include('apps.evacuation.urls')),
    path('', include('apps.assistant.urls')),
    path('', include('apps.satellite.urls')),
    path('', include('apps.fire.urls')),
    path('', include('apps.alerts.urls')),
    path('', include('apps.reports.urls')),
    path('', include('demo.urls')),
]

handler404 = 'apps.core.views.custom_404_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
