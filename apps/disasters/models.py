from django.db import models

class Disaster(models.Model):
    TYPE_CHOICES = [
        ('FLOOD', 'Flood & Inundation'),
        ('WILDFIRE', 'Wildfire / Forest Fire'),
        ('CYCLONE', 'Cyclone & Coastal Surge'),
        ('HEAVY_RAINFALL', 'Extreme Heavy Rainfall'),
        ('LANDSLIDE', 'Landslide / Debris Flow'),
    ]

    SEVERITY_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MODERATE', 'Moderate Risk'),
        ('HIGH', 'High Alert'),
        ('CRITICAL', 'Critical Emergency'),
    ]

    STATUS_CHOICES = [
        ('MONITORING', 'Monitoring Stage'),
        ('ACTIVE', 'Active Response Stage'),
        ('CONTAINED', 'Contained'),
        ('RESOLVED', 'Resolved & Recovery'),
    ]

    title = models.CharField(max_length=200)
    disaster_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='FLOOD')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='HIGH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    location_name = models.CharField(max_length=200, default='Bhubaneswar Urban & Riverine Zone')
    state = models.CharField(max_length=100, default='Odisha')
    district = models.CharField(max_length=100, default='Khordha')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    radius_km = models.FloatField(default=12.5)
    affected_area_sqkm = models.FloatField(default=45.8)
    exposed_population = models.IntegerField(default=18500)
    risk_score = models.IntegerField(default=84)
    rainfall_24h_mm = models.FloatField(default=186.4)
    river_water_level_m = models.FloatField(default=14.2)
    danger_water_level_m = models.FloatField(default=15.0)
    description = models.TextField(blank=True)
    is_demo = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Disaster Event'
        verbose_name_plural = 'Disaster Events'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.get_disaster_type_display()} - {self.get_severity_display()})"

class DisasterTimeline(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, related_name='timeline')
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity_level = models.CharField(max_length=20, choices=Disaster.SEVERITY_CHOICES, default='HIGH')
    action_taken = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.title} [{self.timestamp}]"
