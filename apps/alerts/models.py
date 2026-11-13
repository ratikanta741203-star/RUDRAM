from django.db import models
from apps.disasters.models import Disaster
from django.contrib.auth.models import User

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('INFO', 'Informational Notice'),
        ('WARNING', 'Warning / Yellow Alert'),
        ('HIGH', 'High Alert / Orange Alert'),
        ('CRITICAL', 'Critical Flash Flood Emergency / Red Alert'),
    ]

    disaster = models.ForeignKey(Disaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='CRITICAL')
    disaster_type = models.CharField(max_length=50, default='FLOOD')
    location_name = models.CharField(max_length=200, default='Bhubaneswar Urban Sector')
    latitude = models.FloatField(default=20.2961)
    longitude = models.FloatField(default=85.8245)
    recommended_action = models.TextField(default='Move to designated high-ground shelters immediately.')
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=150, default='RUDRAM Automated AI Early Warning System')
    broadcast_channels = models.CharField(max_length=150, default='SMS, CAP Siren, Mobile App, Radio')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title} ({self.created_at})"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification: {self.title}"

class AlertApprovalRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Admin Approval'),
        ('APPROVED', 'Approved by Admin'),
        ('REJECTED', 'Rejected by Admin'),
    ]

    ACTION_CHOICES = [
        ('CREATE', 'Create Emergency Alert'),
        ('EDIT', 'Edit Existing Alert'),
        ('DEACTIVATE', 'Deactivate Alert'),
    ]

    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_approval_requests')
    requested_action = models.CharField(max_length=30, choices=ACTION_CHOICES, default='CREATE')
    alert = models.ForeignKey(Alert, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_requests')
    title = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField(blank=True, default='')
    severity = models.CharField(max_length=20, default='CRITICAL')
    disaster_type = models.CharField(max_length=50, default='FLOOD')
    location_name = models.CharField(max_length=200, default='')
    recommended_action = models.TextField(blank=True, default='')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_alert_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Request by {self.operator.username}: [{self.requested_action}] - {self.status}"

