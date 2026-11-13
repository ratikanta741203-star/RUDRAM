from django.contrib import admin
from apps.alerts.models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'location_name', 'is_active', 'source', 'created_at')
    list_filter = ('severity', 'is_active', 'disaster_type')
    search_fields = ('title', 'message', 'location_name')
