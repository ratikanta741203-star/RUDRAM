from django.urls import path
from apps.satellite import views

urlpatterns = [
    path('satellite/', views.satellite_view, name='satellite'),
    path('api/satellite/search/', views.SatelliteSearchAPIView.as_view(), name='api_satellite_search'),
    path('api/satellite/flood-detection/', views.SatelliteFloodDetectionAPIView.as_view(), name='api_satellite_flood'),
    path('api/satellite/change-detection/', views.SatelliteChangeDetectionAPIView.as_view(), name='api_satellite_change'),
    path('api/satellite/damage-detection/', views.SatelliteDamageDetectionAPIView.as_view(), name='api_satellite_damage'),
]
