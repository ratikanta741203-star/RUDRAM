from django.contrib import admin
from apps.population.models import PopulationExposure

@admin.register(PopulationExposure)
class PopulationExposureAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'total_population', 'exposed_population', 'vulnerable_population', 'critical_risk_population', 'exposure_score', 'source', 'updated_at')
    list_filter = ('source', 'is_demo')
    search_fields = ('zone_name', 'district')
