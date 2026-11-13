from django.db import models
from apps.disasters.models import Disaster

class RiskZone(models.Model):
    LEVEL_CHOICES = [
        ('LOW', 'Low Risk (0-30%)'),
        ('MODERATE', 'Moderate Risk (31-60%)'),
        ('HIGH', 'High Risk (61-80%)'),
        ('CRITICAL', 'Critical Emergency (81-100%)'),
    ]

    name = models.CharField(max_length=150)
    district = models.CharField(max_length=100, default='Khordha')
    state = models.CharField(max_length=100, default='Odisha')
    risk_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='HIGH')
    risk_score = models.IntegerField(default=75)
    center_lat = models.FloatField(default=20.2961)
    center_lon = models.FloatField(default=85.8245)
    polygon_geojson = models.JSONField(blank=True, null=True)
    population_count = models.IntegerField(default=5400)
    vulnerable_buildings = models.IntegerField(default=420)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-risk_score']

    def __str__(self):
        return f"{self.name} - {self.risk_level} ({self.risk_score}%)"

class RiskPrediction(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='predictions')
    location_name = models.CharField(max_length=200, default='Bhubaneswar Urban Region')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    
    # Hydrological & Environmental features
    rainfall_current_mm = models.FloatField(default=15.0)
    rainfall_24h_mm = models.FloatField(default=186.4)
    rainfall_7d_mm = models.FloatField(default=340.0)
    rainfall_forecast_24h_mm = models.FloatField(default=95.0)
    temperature_c = models.FloatField(default=27.5)
    humidity_pct = models.FloatField(default=92.0)
    wind_speed_kmh = models.FloatField(default=35.0)
    elevation_m = models.FloatField(default=14.0)
    slope_deg = models.FloatField(default=1.8)
    distance_to_water_km = models.FloatField(default=0.8)
    river_water_level_m = models.FloatField(default=14.5)
    
    # Model inference outputs
    risk_score = models.FloatField(default=87.5)
    risk_level = models.CharField(max_length=20, default='CRITICAL')
    confidence = models.FloatField(default=0.91)
    model_mode = models.CharField(max_length=50, default='XGBOOST_ENSEMBLE')
    is_demo = models.BooleanField(default=False)
    recommended_action = models.TextField(default='Immediate evacuation of vulnerable riverine settlements.')
    contributing_factors = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction @ {self.location_name}: {self.risk_level} ({self.risk_score}%)"
