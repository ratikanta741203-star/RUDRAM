from django.contrib import admin
from apps.risk.models import RiskPrediction, RiskZone

@admin.register(RiskZone)
class RiskZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_level', 'risk_score', 'population_count', 'vulnerable_buildings', 'is_active', 'updated_at')
    list_filter = ('risk_level', 'is_active')
    search_fields = ('name', 'district')

@admin.register(RiskPrediction)
class RiskPredictionAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'risk_level', 'risk_score', 'rainfall_24h_mm', 'elevation_m', 'model_mode', 'is_demo', 'created_at')
    list_filter = ('risk_level', 'model_mode', 'is_demo')
    search_fields = ('location_name',)
