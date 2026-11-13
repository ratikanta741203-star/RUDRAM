from django.contrib import admin
from apps.fire.models import FireHotspot

@admin.register(FireHotspot)
class FireHotspotAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'confidence', 'frp_mw', 'satellite', 'scan_time')
    list_filter = ('satellite', 'is_demo')
