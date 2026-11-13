from django.urls import path
from apps.weather import views

urlpatterns = [
    path('api/weather/current/', views.CurrentWeatherAPIView.as_view(), name='api_weather_current'),
    path('api/weather/forecast/', views.ForecastWeatherAPIView.as_view(), name='api_weather_forecast'),
    path('api/weather/india/', views.IndiaLiveWeatherAPIView.as_view(), name='api_weather_india'),
    path('api/weather/state/', views.StateDistrictsLiveWeatherAPIView.as_view(), name='api_weather_state'),
    path('api/weather/state/<str:state_code>/', views.StateDistrictsLiveWeatherAPIView.as_view(), name='api_weather_state_code'),
    path('api/rainfall/', views.RainfallTrendAPIView.as_view(), name='api_rainfall'),
    path('api/rainfall/gpm/', views.GpmRainfallAPIView.as_view(), name='api_rainfall_gpm'),
    path('api/location/search/', views.GeocodeLocationAPIView.as_view(), name='api_location_search'),
    path('api/location/geocode/', views.GeocodeAddressAPIView.as_view(), name='api_location_geocode'),
]
