from django.contrib import admin
from apps.disasters.models import Disaster, DisasterTimeline

class DisasterTimelineInline(admin.TabularInline):
    model = DisasterTimeline
    extra = 1

@admin.register(Disaster)
class DisasterAdmin(admin.ModelAdmin):
    list_display = ('title', 'disaster_type', 'severity', 'status', 'location_name', 'risk_score', 'exposed_population', 'is_demo', 'updated_at')
    list_filter = ('disaster_type', 'severity', 'status', 'is_demo')
    search_fields = ('title', 'location_name', 'district', 'state')
    inlines = [DisasterTimelineInline]
