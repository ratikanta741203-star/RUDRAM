from django.contrib import admin
from apps.reports.models import GeneratedReport

@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'report_format', 'location_name', 'generated_by', 'created_at')
    list_filter = ('report_type', 'report_format')
