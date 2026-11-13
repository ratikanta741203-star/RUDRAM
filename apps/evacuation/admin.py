from django.contrib import admin
from apps.evacuation.models import EvacuationRoute

@admin.register(EvacuationRoute)
class EvacuationRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin_name', 'destination_name', 'distance_km', 'safety_score', 'risk_level', 'is_recommended')
    list_filter = ('is_recommended', 'risk_level')
