from django.contrib import admin
from apps.weather.models import WeatherObservation, RainfallObservation

@admin.register(WeatherObservation)
class WeatherObservationAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'temperature_c', 'rainfall_24h_mm', 'humidity_pct', 'source', 'is_demo', 'timestamp')
    list_filter = ('source', 'is_demo')

@admin.register(RainfallObservation)
class RainfallObservationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'rainfall_1h_mm', 'rainfall_24h_mm', 'rainfall_7d_mm', 'source', 'recorded_at')
