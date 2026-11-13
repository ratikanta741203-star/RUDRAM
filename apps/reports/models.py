from django.db import models

class GeneratedReport(models.Model):
    REPORT_TYPES = [
        ('DISASTER_SUMMARY', 'Comprehensive Disaster Situation Report'),
        ('FLOOD_RISK', 'AI Flood Risk & Catchment Vulnerability Report'),
        ('SHELTER_EVACUATION', 'Evacuation & Shelter Logistics Report'),
        ('SATELLITE_DAMAGE', 'Satellite SAR Inundation & Damage Assessment'),
    ]

    FORMAT_CHOICES = [
        ('PDF', 'Portable Document Format (.pdf)'),
        ('CSV', 'Comma-Separated Values (.csv)'),
        ('GEOJSON', 'Geospatial Vector GeoJSON (.json)'),
    ]

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, default='DISASTER_SUMMARY')
    report_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='PDF')
    location_name = models.CharField(max_length=150, default='Bhubaneswar, Odisha')
    generated_by = models.CharField(max_length=150, default='System Administrator')
    summary_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.report_format}) - {self.created_at}"

# Alias for standard naming convention
Report = GeneratedReport
