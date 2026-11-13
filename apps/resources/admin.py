from django.contrib import admin
from apps.resources.models import Resource, ResourceAllocation, RescueTeam

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity_available', 'quantity_required', 'quantity_allocated', 'unit')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('resource', 'quantity', 'destination_zone', 'status', 'requester_name', 'created_at')
    list_filter = ('status',)

@admin.register(RescueTeam)
class RescueTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_type', 'status', 'members_count', 'contact_phone', 'lead_officer')
    list_filter = ('team_type', 'status')
