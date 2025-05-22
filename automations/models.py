from django.db import models

# Create your models here.

class AutomatedProcess(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    script_path = models.CharField(max_length=1024)
    virtual_env_path = models.CharField(max_length=1024, blank=True, null=True)
    cron_schedule = models.CharField(max_length=100, blank=True, null=True)
    last_run_time = models.DateTimeField(blank=True, null=True)
    last_run_status = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProcessLog(models.Model):
    STATUS_CHOICES = [
        ('STARTED', 'Iniciado'),
        ('RUNNING', 'Corriendo'),
        ('SUCCESS', 'Exitoso'),
        ('FAILED', 'Fallido'),
    ]
    process = models.ForeignKey(AutomatedProcess, on_delete=models.CASCADE, related_name='logs')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')
    output_log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.process.name} - {self.start_time.strftime("%Y-%m-%d %H:%M:%S")} - {self.status}'

    class Meta:
        ordering = ['-start_time']
