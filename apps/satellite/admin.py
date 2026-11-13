from django.contrib import admin
from apps.satellite.models import SatelliteAnalysis, DamageZone

@admin.register(SatelliteAnalysis)
class SatelliteAnalysisAdmin(admin.ModelAdmin):
    list_display = ('title', 'sensor', 'status', 'flooded_area_sqkm', 'affected_population', 'confidence', 'is_demo', 'created_at')
    list_filter = ('sensor', 'status', 'is_demo')
