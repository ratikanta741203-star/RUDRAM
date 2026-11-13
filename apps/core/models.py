from django.db import models

class DataSourceStatus(models.Model):
    STATUS_CHOICES = [
        ('CONNECTED', 'Connected (Live)'),
        ('DEMO', 'Demo Simulation Mode'),
        ('TEMPORARILY_UNAVAILABLE', 'Temporarily Unavailable (Cached)'),
        ('NOT_CONFIGURED', 'Not Configured'),
        ('ERROR', 'Error'),
    ]

    source_name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, default='API')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DEMO')
    endpoint_url = models.CharField(max_length=255, blank=True, null=True)
    is_live = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    last_ping = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    response_time_ms = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Data Source Status'
        verbose_name_plural = 'Data Source Statuses'
        ordering = ['source_name']

    def __str__(self):
        return f"{self.display_name} [{self.status}]"

class AuditLog(models.Model):
    user_name = models.CharField(max_length=150, default='System / Anonymous')
    action = models.CharField(max_length=200)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} - {self.action} ({self.created_at})"

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"{self.key}: {self.value}"

def get_global_demo_mode():
    from django.conf import settings
    try:
        setting = SystemSetting.objects.filter(key='DEMO_MODE').first()
        if setting:
            is_demo = setting.value.lower() in ('true', '1', 't', 'yes')
            settings.DEMO_MODE = is_demo
            return is_demo
    except Exception:
        pass
    return getattr(settings, 'DEMO_MODE', False)

def set_global_demo_mode(is_demo: bool):
    from django.conf import settings
    val_str = 'True' if is_demo else 'False'
    try:
        SystemSetting.objects.update_or_create(key='DEMO_MODE', defaults={'value': val_str})
    except Exception as e:
        print("SystemSetting error:", e)
    settings.DEMO_MODE = is_demo

