from django.db import models

class Shelter(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open & Accepting Evacuees'),
        ('NEAR_CAPACITY', 'Near Full Capacity (>80%)'),
        ('FULL', 'Full / Maximum Capacity Reached'),
        ('CLOSED', 'Closed / Inactive'),
    ]

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, default='Bhubaneswar, Odisha')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    total_capacity = models.IntegerField(default=1200)
    current_occupancy = models.IntegerField(default=450)
    
    # Essential resources on-site
    has_potable_water = models.BooleanField(default=True)
    has_food_stocks = models.BooleanField(default=True)
    has_medical_station = models.BooleanField(default=True)
    has_backup_generator = models.BooleanField(default=True)
    has_disability_access = models.BooleanField(default=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    contact_person = models.CharField(max_length=150, default='District Relief Officer')
    phone_number = models.CharField(max_length=30, default='0674-2391077')
    elevation_m = models.FloatField(default=32.0)
    current_flood_risk = models.CharField(max_length=20, default='LOW')
    is_demo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def available_capacity(self):
        return max(0, self.total_capacity - self.current_occupancy)

    @property
    def occupancy_percentage(self):
        if self.total_capacity == 0:
            return 0
        return round((self.current_occupancy / self.total_capacity) * 100, 1)

    def __str__(self):
        return f"{self.name} [{self.current_occupancy}/{self.total_capacity} - {self.status}]"
