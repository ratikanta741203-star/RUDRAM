from django.urls import path
from apps.shelters import views

urlpatterns = [
    path('shelters/', views.shelters_view, name='shelters'),
    path('api/shelters/', views.ShelterListAPIView.as_view(), name='api_shelters'),
    path('api/shelters/recommend/', views.ShelterRecommendAPIView.as_view(), name='api_shelters_recommend'),
    path('api/shelters/nearby/', views.NearbySheltersAPIView.as_view(), name='api_shelters_nearby'),
    path('api/shelters/<int:pk>/update-occupancy/', views.ShelterUpdateOccupancyAPIView.as_view(), name='api_shelter_update_occ'),
    path('api/location/geocode/', views.GeocodeShelterLocationAPIView.as_view(), name='api_location_geocode'),
    path('api/shelters/geocode/', views.GeocodeShelterLocationAPIView.as_view(), name='api_shelters_geocode'),
    path('api/location/search/', views.SmartLocationSearchAPIView.as_view(), name='api_smart_location_search'),
    path('api/shelters/location-search/', views.SmartLocationSearchAPIView.as_view(), name='api_shelters_location_search'),
]
