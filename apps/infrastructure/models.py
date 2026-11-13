from django.db import models

class Infrastructure(models.Model):
    TYPE_CHOICES = [
        ('HOSPITAL', 'Hospital / Trauma Centre'),
        ('FIRE_STATION', 'Fire & Rescue Station'),
        ('POLICE', 'Police Station'),
        ('SCHOOL', 'School / Relief Camp Site'),
        ('POWER_STATION', 'Substation / Electrical Grid'),
        ('TELECOM', 'Telecom Tower / Communication Node'),
        ('BRIDGE', 'River Bridge / Flyover'),
        ('ROAD', 'Highway / Evacuation Roadway'),
        ('OTHER', 'Other Critical Asset'),
    ]

    STATUS_CHOICES = [
        ('OPERATIONAL', 'Fully Operational'),
        ('IMPACTED', 'Partially Impacted'),
        ('SUBMERGED', 'Submerged / Inaccessible'),
        ('EVACUATED', 'Evacuated'),
    ]

    name = models.CharField(max_length=200)
    infra_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='HOSPITAL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERATIONAL')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    capacity = models.IntegerField(default=200)
    contact_phone = models.CharField(max_length=30, default='112')
    is_backup_power_ready = models.BooleanField(default=True)
    elevation_m = models.FloatField(default=24.0)
    is_demo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_infra_type_display()} - {self.get_status_display()})"

class Road(models.Model):
    name = models.CharField(max_length=200)
    road_number = models.CharField(max_length=50, default='NH 16')
    is_passable = models.BooleanField(default=True)
    current_water_depth_m = models.FloatField(default=0.0)
    safety_score = models.IntegerField(default=90)
    elevation_m = models.FloatField(default=25.0)
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} [{self.road_number}]"

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    total_beds = models.IntegerField(default=500)
    icu_available = models.IntegerField(default=45)
    emergency_phone = models.CharField(max_length=30, default='0674-2476789')
    is_operational = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PoliceStation(models.Model):
    name = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=150, default='Bhubaneswar Urban')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    phone = models.CharField(max_length=30, default='112')
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class FireStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    amphibious_vehicles = models.IntegerField(default=2)
    rescue_boats = models.IntegerField(default=4)
    emergency_phone = models.CharField(max_length=30, default='101')
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class School(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    shelter_capacity = models.IntegerField(default=600)
    has_clean_water = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CriticalInfrastructure(models.Model):
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, default='Power & Grid')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    backup_generators_ready = models.BooleanField(default=True)
    status = models.CharField(max_length=50, default='OPERATIONAL')
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.sector})"

class River(models.Model):
    name = models.CharField(max_length=150)
    basin = models.CharField(max_length=150, default='Mahanadi Basin')
    current_water_level_m = models.FloatField(default=14.2)
    warning_level_m = models.FloatField(default=13.8)
    danger_level_m = models.FloatField(default=15.0)
    trend = models.CharField(max_length=30, default='RISING (+0.12 m/hr)')
    coordinates_geojson = models.JSONField(blank=True, null=True)
    is_demo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} River (Level: {self.current_water_level_m}m)"

class Dam(models.Model):
    name = models.CharField(max_length=150)
    river_name = models.CharField(max_length=150, default='Mahanadi')
    latitude = models.FloatField(default=20.5284)
    longitude = models.FloatField(default=85.7984)
    current_reservoir_level_ft = models.FloatField(default=628.4)
    full_reservoir_level_ft = models.FloatField(default=630.0)
    inflow_cusecs = models.FloatField(default=450000)
    outflow_cusecs = models.FloatField(default=410000)
    gates_open = models.IntegerField(default=18)
    total_gates = models.IntegerField(default=64)
    status_alert = models.CharField(max_length=50, default='HIGH ALERT')
    is_demo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} Dam ({self.gates_open}/{self.total_gates} Gates Open)"

class Canal(models.Model):
    name = models.CharField(max_length=150)
    discharge_capacity_cusecs = models.FloatField(default=3500)
    current_flow_cusecs = models.FloatField(default=3200)
    status = models.CharField(max_length=50, default='NEAR CAPACITY')
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Bridge(models.Model):
    name = models.CharField(max_length=150)
    river_crossed = models.CharField(max_length=150, default='Kuakhai River')
    latitude = models.FloatField(default=20.3120)
    longitude = models.FloatField(default=85.8480)
    clearance_above_water_m = models.FloatField(default=1.4)
    is_passable = models.BooleanField(default=True)
    structural_alert = models.CharField(max_length=100, default='Submerged Approach Warning')
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Passable: {self.is_passable})"
