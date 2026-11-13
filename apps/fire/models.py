from django.db import models

class FireHotspot(models.Model):
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    brightness = models.FloatField(default=335.2)
    scan_time = models.DateTimeField(auto_now_add=True)
    confidence = models.IntegerField(default=85)
    satellite = models.CharField(max_length=50, default='VIIRS NOAA-20')
    frp_mw = models.FloatField(default=32.4)
    hotspot_type = models.CharField(max_length=100, default='Vegetation Thermal Anomaly')
    is_demo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-scan_time']

    def __str__(self):
        return f"Fire Hotspot ({self.latitude}, {self.longitude}) - Conf: {self.confidence}%"
