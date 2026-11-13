from django.contrib import admin
from apps.infrastructure.models import Infrastructure, River, Dam, Canal, Bridge

@admin.register(Infrastructure)
class InfrastructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'infra_type', 'status', 'capacity', 'elevation_m', 'contact_phone')
    list_filter = ('infra_type', 'status', 'is_backup_power_ready')
    search_fields = ('name',)

@admin.register(River)
class RiverAdmin(admin.ModelAdmin):
    list_display = ('name', 'basin', 'current_water_level_m', 'danger_level_m', 'trend')

@admin.register(Dam)
class DamAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_reservoir_level_ft', 'gates_open', 'total_gates', 'status_alert')

@admin.register(Bridge)
class BridgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'river_crossed', 'clearance_above_water_m', 'is_passable', 'structural_alert')
