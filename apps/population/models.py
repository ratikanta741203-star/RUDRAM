from django.db import models

class PopulationExposure(models.Model):
    zone_name = models.CharField(max_length=150, default='Bhubaneswar Central Catchment')
    district = models.CharField(max_length=100, default='Khordha')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    radius_km = models.FloatField(default=10.0)
    total_population = models.IntegerField(default=128500)
    exposed_population = models.IntegerField(default=18400)
    vulnerable_population = models.IntegerField(default=5150) # elderly, pregnant women, infants
    critical_risk_population = models.IntegerField(default=3200) # living in zero-buffer riverbanks
    density_per_sqkm = models.FloatField(default=4120.0)
    shelter_deficit_count = models.IntegerField(default=1800)
    exposure_score = models.IntegerField(default=78)
    source = models.CharField(max_length=150, default='WorldPop / Census of India Baseline')
    is_demo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Population Exposure Zone'
        ordering = ['-exposure_score']

    def __str__(self):
        return f"{self.zone_name} - {self.exposed_population} exposed ({self.exposure_score}%)"
