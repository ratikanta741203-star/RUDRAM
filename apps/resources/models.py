from django.db import models
from django.contrib.auth.models import User
from apps.disasters.models import Disaster

class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Ration & Dry Food Packets'),
        ('WATER', 'Potable Drinking Water (Liters)'),
        ('MEDICINE', 'Emergency Medical Kits / ORS'),
        ('BLANKETS', 'Blankets & Tarpaulins'),
        ('RESCUE_BOATS', 'Inflatable Motor Rescue Boats'),
        ('VEHICLES', '4x4 Amphibious & High-Clearance Trucks'),
        ('FIRST_AID', 'Trauma & First Aid Kits'),
        ('PUMPS', 'High-Discharge De-watering Pumps'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='WATER')
    quantity_available = models.IntegerField(default=5000)
    quantity_required = models.IntegerField(default=8500)
    quantity_allocated = models.IntegerField(default=2200)
    unit = models.CharField(max_length=50, default='Units / Kits')
    warehouse_location = models.CharField(max_length=200, default='State Relief Storage Facility, Rasulgarh')
    critical_threshold = models.IntegerField(default=1000)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def remaining_deficit(self):
        return max(0, self.quantity_required - (self.quantity_available + self.quantity_allocated))

    def __str__(self):
        return f"{self.name} ({self.quantity_available} {self.unit} available)"

class ResourceAllocation(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested by Field Officer'),
        ('APPROVED', 'Approved by Emergency Commander'),
        ('DISPATCHED', 'In-Transit / Dispatched'),
        ('DELIVERED', 'Delivered at Relief Center'),
    ]

    disaster = models.ForeignKey(Disaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocations')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='allocations')
    quantity = models.IntegerField(default=500)
    destination_zone = models.CharField(max_length=200, default='Zone A - Rasulgarh Low-Lying Sector')
    requester_name = models.CharField(max_length=150, default='Zone Incident Commander')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='APPROVED')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity} {self.resource.unit} to {self.destination_zone} [{self.status}]"

class RescueTeam(models.Model):
    TEAM_TYPE_CHOICES = [
        ('NDRF', 'NDRF (National Disaster Response Force)'),
        ('ODRAF', 'ODRAF (Odisha Disaster Rapid Action Force)'),
        ('FIRE_RESCUE', 'State Fire & Life Rescue Service'),
        ('MEDICAL_RAPID', 'Mobile Medical Emergency Unit'),
        ('VOLUNTEER', 'Civil Defence & Community Volunteers'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available & Staged'),
        ('DEPLOYED', 'Deployed in Active Zone'),
        ('BUSY', 'Engaged in Rescue Ops'),
        ('OFFLINE', 'Resting / Demobilized'),
    ]

    name = models.CharField(max_length=150)
    team_type = models.CharField(max_length=30, choices=TEAM_TYPE_CHOICES, default='ODRAF')
    members_count = models.IntegerField(default=24)
    lead_officer = models.CharField(max_length=150, default='Commandant S. Patnaik')
    contact_phone = models.CharField(max_length=30, default='94370-11200')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='AVAILABLE')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    equipment_summary = models.CharField(max_length=255, default='4 Motor Boats, Deep-dive gear, Life-lines, Satellite Radio')
    assigned_disaster = models.ForeignKey(Disaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='rescue_teams')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} [{self.get_team_type_display()} - {self.status}]"


class ApprovalRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('RESOURCE_DISPATCH', 'Resource Dispatch Request'),
        ('RESOURCE_STOCK_UPDATE', 'Resource Stock / Quantity Update'),
        ('RESOURCE_CREATE', 'New Resource Stock Creation'),
        ('TEAM_STATUS_UPDATE', 'Rescue Team Status Update'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Admin Approval'),
        ('APPROVED', 'Approved by Admin'),
        ('REJECTED', 'Rejected by Admin'),
    ]

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES)
    target_model = models.CharField(max_length=50)
    target_object_id = models.IntegerField(null=True, blank=True)
    target_object_name = models.CharField(max_length=200, blank=True)
    requested_changes = models.JSONField(default=dict)
    current_values = models.JSONField(default=dict)
    reason = models.TextField(blank=True, default='Emergency operational requirement')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_approvals')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.get_request_type_display()} by {self.requested_by.username}"

