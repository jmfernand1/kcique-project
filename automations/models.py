from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

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

class ScheduledTask(models.Model):
    """
    Modelo para que los usuarios definan tareas programadas de forma sencilla,
    vinculado a un Proceso Automatizado existente.
    """
    FRECUENCIA_CHOICES = (
        ('MINUTOS', 'Cada X Minutos'),
        ('HORAS', 'Cada X Horas'),
        ('DIARIO', 'Diario'),
        ('SEMANAL', 'Semanal'),
        ('MENSUAL', 'Mensual'),
        ('UNA_VEZ', 'Una Sola Vez'),
    )

    DIAS_SEMANA_CHOICES = (
        (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'),
        (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo'),
    )

    process = models.ForeignKey(AutomatedProcess, on_delete=models.CASCADE, related_name='scheduled_tasks', help_text="El proceso que se ejecutará.")
    
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIA_CHOICES, default='DIARIO')
    
    intervalo = models.PositiveIntegerField(blank=True, null=True, help_text="Ej: 15 (para 'Cada 15 Minutos')")
    hora_ejecucion = models.TimeField(help_text="La hora en que se debe ejecutar la tarea.", null=True, blank=True)
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES, null=True, blank=True, help_text="El día de la semana para ejecuciones semanales.")
    dia_mes = models.IntegerField(null=True, blank=True, help_text="El día del mes (1-31) para ejecuciones mensuales.")
    fecha_ejecucion_unica = models.DateTimeField(null=True, blank=True, help_text="La fecha y hora para una ejecución única.")
    
    # Rango de horas de ejecución (solo para MINUTOS y HORAS)
    hora_inicio = models.TimeField(null=True, blank=True, help_text="Hora de inicio del rango permitido para ejecución (solo para tareas por minutos/horas).")
    hora_fin = models.TimeField(null=True, blank=True, help_text="Hora de fin del rango permitido para ejecución (solo para tareas por minutos/horas).")

    activo = models.BooleanField(default=True, help_text="Desmarque para desactivar esta tarea sin eliminarla.")
    
    # Enlace a la tarea real en django-q
    id_tarea_django_q = models.CharField(max_length=100, blank=True, editable=False)

    def __str__(self):
        return f"Programación para '{self.process.name}'"

    def get_resumen_programacion(self):
        """Genera un resumen legible de la programación."""
        if not self.activo:
            return "Inactiva"
        
        if self.frecuencia == 'UNA_VEZ':
            if self.fecha_ejecucion_unica:
                return f"Una vez, el {self.fecha_ejecucion_unica.strftime('%d/%m/%Y a las %H:%M')}"
            return "Una vez (fecha no definida)"
        if self.frecuencia in ['MINUTOS', 'HORAS']:
            unidad = "minutos" if self.frecuencia == 'MINUTOS' else "horas"
            resultado = f"Cada {self.intervalo or 'N/A'} {unidad}"
            if self.hora_inicio and self.hora_fin:
                resultado += f" (solo de {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')})"
            return resultado
        if self.frecuencia == 'DIARIO':
            return f"Todos los días a las {self.hora_ejecucion.strftime('%H:%M') if self.hora_ejecucion else 'N/A'}"
        if self.frecuencia == 'SEMANAL':
            dia = self.get_dia_semana_display() or 'N/A'
            return f"Semanalmente, los {dia} a las {self.hora_ejecucion.strftime('%H:%M') if self.hora_ejecucion else 'N/A'}"
        if self.frecuencia == 'MENSUAL':
            return f"Mensualmente, el día {self.dia_mes or 'N/A'} a las {self.hora_ejecucion.strftime('%H:%M') if self.hora_ejecucion else 'N/A'}"
        
        return "Configuración incompleta"

    class Meta:
        verbose_name = "Tarea Programada"
        verbose_name_plural = "Tareas Programadas"
        ordering = ['process__name']


def reset_scheduled_tasks_on_startup():
    """
    Función para reiniciar las fechas de las tareas programadas al arrancar la aplicación.
    Actualiza las fechas de próxima ejecución de todas las tareas activas para evitar
    que se ejecuten múltiples veces tratando de 'ponerse al día'.
    """
    from django_q.models import Schedule
    from django_q.tasks import schedule
    
    print(f"[{timezone.now()}] Reiniciando tareas programadas al arrancar la aplicación...")
    
    # Obtener todas las tareas activas
    tareas_activas = ScheduledTask.objects.filter(activo=True)
    tareas_reiniciadas = 0
    
    for tarea in tareas_activas:
        try:
            # Eliminar la tarea anterior de Django-Q si existe
            if tarea.id_tarea_django_q:
                Schedule.objects.filter(name=tarea.id_tarea_django_q).delete()
            
            # Reprogramar la tarea con fecha/hora actual
            from automations.views import _programar_en_django_q
            _programar_en_django_q(tarea)
            
            if tarea.frecuencia not in ['UNA_VEZ']:
                print(f"  - Reiniciada: {tarea.process.name} ({tarea.get_resumen_programacion()})")
                tareas_reiniciadas += 1
                
        except Exception as e:
            print(f"  - Error al reiniciar tarea {tarea.process.name}: {e}")
    
    print(f"[{timezone.now()}] Reinicio completado. {tareas_reiniciadas} tareas reiniciadas.")
