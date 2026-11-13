from django.db import models

class WeatherObservation(models.Model):
    station_name = models.CharField(max_length=150, default='Bhubaneswar IMD Observatory')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    temperature_c = models.FloatField(default=28.4)
    humidity_pct = models.FloatField(default=88.0)
    rainfall_current_mm = models.FloatField(default=14.2)
    rainfall_24h_mm = models.FloatField(default=186.4)
    wind_speed_kmh = models.FloatField(default=32.0)
    wind_direction_deg = models.FloatField(default=150.0)
    surface_pressure_hpa = models.FloatField(default=998.5)
    weather_condition = models.CharField(max_length=100, default='Heavy Torrential Rain')
    source = models.CharField(max_length=100, default='Open-Meteo API')
    is_demo = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.station_name} @ {self.timestamp}: {self.rainfall_24h_mm}mm"

class RainfallObservation(models.Model):
    location_name = models.CharField(max_length=150, default='Bhubaneswar Station')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    rainfall_1h_mm = models.FloatField(default=18.5)
    rainfall_3h_mm = models.FloatField(default=48.2)
    rainfall_6h_mm = models.FloatField(default=92.0)
    rainfall_12h_mm = models.FloatField(default=145.0)
    rainfall_24h_mm = models.FloatField(default=186.4)
    rainfall_7d_mm = models.FloatField(default=380.0)
    source = models.CharField(max_length=100, default='GPM IMERG / Open-Meteo')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
