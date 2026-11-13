from django.contrib import admin
from apps.assistant.models import EmergencyRecommendation

@admin.register(EmergencyRecommendation)
class EmergencyRecommendationAdmin(admin.ModelAdmin):
    list_display = ('priority', 'situation_summary', 'operator_overridden', 'created_at')
    list_filter = ('priority', 'operator_overridden')
