from django.db import models

# Create your models here.

class CasoDebito(models.Model):
    cod_caso_bizagi = models.CharField(max_length=255, unique=True, help_text="Código único del caso en Bizagi.")
    num_prestamo = models.CharField(max_length=255, blank=True, null=True, help_text="Número de préstamo asociado al caso.")
    docsoldv = models.CharField(max_length=255, blank=True, null=True, help_text="Documentos solicitados o validados.")
    tipo_de_cuenta = models.CharField(max_length=100, blank=True, null=True, help_text="Tipo de cuenta (ahorros, corriente, etc.).")
    numcta_debito = models.CharField(max_length=255, blank=True, null=True, help_text="Número de cuenta para débito.")
    secuencia_cta = models.CharField(max_length=100, blank=True, null=True, help_text="Secuencia de la cuenta.")
    codigo_del_banco = models.CharField(max_length=100, blank=True, null=True, help_text="Código del banco.")
    codigo_ciudad = models.CharField(max_length=100, blank=True, null=True, help_text="Código de la ciudad.")
    estado = models.CharField(max_length=100, default='PENDIENTE', help_text="Estado actual del caso (PENDIENTE, EN_PROCESO, RESUELTO, ERROR).")

    # Campos para trazabilidad
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora en que se registró el caso.")
    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text="Fecha y hora de la última actualización del caso.")
    fecha_inicio_proceso = models.DateTimeField(blank=True, null=True, help_text="Fecha y hora en que se inició el procesamiento del caso.")
    fecha_fin_proceso = models.DateTimeField(blank=True, null=True, help_text="Fecha y hora en que finalizó el procesamiento del caso.")
    
    # Campos para identificar los procesos Python
    proceso_creador = models.CharField(max_length=255, blank=True, null=True, help_text="Identificador del script Python que creó el caso.")
    proceso_actualizador = models.CharField(max_length=255, blank=True, null=True, help_text="Identificador del script Python que actualizó el caso por última vez.")
    
    # Otros campos que podrían ser útiles para la trazabilidad
    intentos_procesamiento = models.IntegerField(default=0, help_text="Número de veces que se ha intentado procesar el caso.")
    ultimo_error = models.TextField(blank=True, null=True, help_text="Mensaje del último error ocurrido durante el procesamiento.")
    datos_adicionales = models.JSONField(blank=True, null=True, help_text="Campo para almacenar información adicional en formato JSON.")

    def __str__(self):
        return f"Caso {self.cod_caso_bizagi} - {self.estado}"

    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = "Caso Pendiente"
        verbose_name_plural = "Casos Pendientes"
