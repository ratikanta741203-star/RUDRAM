from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin / Disaster Commander'),
        ('EMERGENCY_OPERATOR', 'Emergency Operator'),
        ('ANALYST', 'GIS & Remote Sensing Analyst'),
        ('CITIZEN', 'Citizen / First Responder'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='CITIZEN')
    phone_number = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=150, blank=True, default='State Disaster Management Authority')
    assigned_zone = models.CharField(max_length=100, blank=True, default='Odisha Coastal Zone')
    preferred_language = models.CharField(max_length=10, default='en')
    latitude = models.FloatField(null=True, blank=True, default=20.2961)
    longitude = models.FloatField(null=True, blank=True, default=85.8245)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role='ADMIN' if instance.is_superuser else 'CITIZEN')
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
