from django.contrib import admin
from apps.core.models import DataSourceStatus, AuditLog

@admin.register(DataSourceStatus)
class DataSourceStatusAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'category', 'status', 'is_live', 'response_time_ms', 'last_updated')
    list_filter = ('status', 'category', 'is_live')
    search_fields = ('source_name', 'display_name')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'action', 'target_model', 'created_at', 'ip_address')
    list_filter = ('target_model', 'created_at')
    search_fields = ('user_name', 'action', 'details')
    readonly_fields = ('created_at',)
