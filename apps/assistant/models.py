from django.db import models
from apps.disasters.models import Disaster

class EmergencyRecommendation(models.Model):
    PRIORITY_CHOICES = [
        ('CRITICAL', 'Critical - Immediate Execution Required'),
        ('HIGH', 'High - Urgent Operations'),
        ('MEDIUM', 'Medium - Precautionary Action'),
    ]

    disaster = models.ForeignKey(Disaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    situation_summary = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='CRITICAL')
    action_items = models.JSONField(default=list)
    rationale = models.TextField(blank=True)
    is_rule_based_demo = models.BooleanField(default=True)
    operator_overridden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Recommendation [{self.priority}] - {self.created_at}"
