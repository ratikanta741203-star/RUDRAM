from django.db import models

class EvacuationRoute(models.Model):
    name = models.CharField(max_length=200, default='Safe Evacuation Artery')
    origin_name = models.CharField(max_length=200, default='Rasulgarh Low-Lying Sector')
    origin_lat = models.FloatField(default=20.2961)
    origin_lon = models.FloatField(default=85.8245)
    destination_name = models.CharField(max_length=200, default='BJB College High-Ground Shelter')
    dest_lat = models.FloatField(default=20.3061)
    dest_lon = models.FloatField(default=85.8445)
    distance_km = models.FloatField(default=6.2)
    estimated_time_min = models.FloatField(default=16.5)
    risk_level = models.CharField(max_length=20, default='LOW')
    safety_score = models.IntegerField(default=92)
    is_recommended = models.BooleanField(default=True)
    waypoints_geojson = models.JSONField(blank=True, null=True)
    hazards_avoided = models.JSONField(blank=True, null=True)
    is_demo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-safety_score']

    def __str__(self):
        return f"{self.name}: {self.origin_name} -> {self.destination_name} (Safety: {self.safety_score}%)"
