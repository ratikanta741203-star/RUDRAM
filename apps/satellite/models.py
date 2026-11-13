from django.db import models

class SatelliteAnalysis(models.Model):
    SENSOR_CHOICES = [
        ('SENTINEL_1', 'Sentinel-1 SAR C-Band Radar'),
        ('SENTINEL_2', 'Sentinel-2 MSI Optical Multi-Spectral'),
        ('FUSION', 'SAR + Optical Multi-Modal Fusion'),
        ('UNET_CNN', 'Deep Learning U-Net Segmentation'),
    ]

    STATUS_CHOICES = [
        ('PROCESSING', 'Processing & Speckle Filtering'),
        ('COMPLETED', 'Completed & Georeferenced'),
        ('FAILED', 'Failed / Insufficient Coverage'),
    ]

    title = models.CharField(max_length=200, default='Sentinel-1 SAR Flood Inundation Analysis')
    sensor = models.CharField(max_length=30, choices=SENSOR_CHOICES, default='SENTINEL_1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    aoi_name = models.CharField(max_length=150, default='Bhubaneswar-Cuttack Flood Basin')
    pre_event_date = models.DateField(default='2026-08-01')
    post_event_date = models.DateField(default='2026-08-14')
    flooded_area_sqkm = models.FloatField(default=28.4)
    damaged_area_sqkm = models.FloatField(default=34.8)
    affected_population = models.IntegerField(default=16200)
    submerged_roads_km = models.FloatField(default=24.6)
    confidence = models.FloatField(default=0.93)
    is_demo = models.BooleanField(default=True)
    metrics = models.JSONField(blank=True, null=True)
    geojson_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.sensor} - {self.status}]"

class DamageZone(models.Model):
    analysis = models.ForeignKey(SatelliteAnalysis, on_delete=models.CASCADE, related_name='damage_zones')
    zone_name = models.CharField(max_length=150)
    damage_severity = models.CharField(max_length=50, default='HIGH')
    area_sqkm = models.FloatField(default=12.4)
    polygon_geojson = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.zone_name} ({self.damage_severity})"
