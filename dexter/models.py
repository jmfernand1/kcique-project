from django.db import models
from django.utils import timezone


# ============================================================================
# MODELOS DE TRACKING/LOG PARA ETL
# ============================================================================

class EjecucionETL(models.Model):
    """
    Modelo para rastrear cada ejecución completa del ETL.
    Permite tener un historial de todas las ejecuciones.
    """
    TIPO_CHOICES = [
        ('DESEMBOLSO', 'Proceso de Desembolso'),
        ('GARANTIA', 'Proceso de Garantía'),
    ]
    
    ESTADO_CHOICES = [
        ('INICIADO', 'Iniciado'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),
        ('PAUSADO', 'Pausado'),
    ]
    
    tipo_proceso = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='INICIADO')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    total_registros = models.IntegerField(default=0)
    registros_procesados = models.IntegerField(default=0)
    registros_exitosos = models.IntegerField(default=0)
    registros_fallidos = models.IntegerField(default=0)
    ultima_etapa_ejecutada = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    mensaje_error = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Ejecución ETL"
        verbose_name_plural = "Ejecuciones ETL"
    
    def __str__(self):
        return f"{self.tipo_proceso} - {self.estado} ({self.fecha_inicio.strftime('%Y-%m-%d %H:%M')})"


class ProcesoDesembolso(models.Model):
    """Tracking de cada desembolso en el proceso ETL"""
    ETAPAS = [
        ('PENDIENTE', 'Pendiente'),
        ('GRABAR_CARGOS_FIJOS', 'Grabar Cargos Fijos'),
        ('DESEMBOLSO', 'Desembolso'),
        ('FRACCIONAR', 'Fraccionar'),
        ('SELECCIONAR_PAGO', 'Seleccionar Pago'),
        ('AUTORIZAR', 'Autorizar'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
    ]
    
    ejecucion = models.ForeignKey(EjecucionETL, on_delete=models.CASCADE, related_name='procesos_desembolso')
    desembolso = models.ForeignKey('Desembolso', on_delete=models.CASCADE, related_name='procesos_etl')
    etapa_actual = models.CharField(max_length=30, choices=ETAPAS, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    intentos = models.IntegerField(default=0)
    mensaje_error = models.TextField(null=True, blank=True)
    datos_etapa = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Proceso de Desembolso"
        verbose_name_plural = "Procesos de Desembolso"
        indexes = [
            models.Index(fields=['etapa_actual']),
            models.Index(fields=['ejecucion', 'etapa_actual']),
        ]
    
    def __str__(self):
        return f"Desembolso {self.desembolso.referencia} - {self.etapa_actual}"


class ProcesoGarantia(models.Model):
    """Tracking de cada garantía en el proceso ETL"""
    ETAPAS = [
        ('PENDIENTE', 'Pendiente'),
        ('GRABAR_INFO_VEHICULO', 'Grabar Info Vehículo'),
        ('GRABAR_INFO_POLIZA', 'Grabar Info Póliza'),
        ('DESAFILIAR_GARANTIA_REPETIDA', 'Desafiliar Garantía Repetida'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
    ]
    
    ejecucion = models.ForeignKey(EjecucionETL, on_delete=models.CASCADE, related_name='procesos_garantia')
    garantia = models.ForeignKey('Garantia', on_delete=models.CASCADE, related_name='procesos_etl')
    etapa_actual = models.CharField(max_length=35, choices=ETAPAS, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    intentos = models.IntegerField(default=0)
    mensaje_error = models.TextField(null=True, blank=True)
    datos_etapa = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Proceso de Garantía"
        verbose_name_plural = "Procesos de Garantía"
        indexes = [
            models.Index(fields=['etapa_actual']),
            models.Index(fields=['ejecucion', 'etapa_actual']),
        ]
    
    def __str__(self):
        return f"Garantía {self.garantia.placa} - {self.etapa_actual}"


# ============================================================================
# MODELOS DE DATOS PRINCIPALES
# ============================================================================

class Desembolso(models.Model):
    referencia = models.CharField(max_length=100, unique=True)
    obligacion = models.BigIntegerField()
    id_cliente = models.BigIntegerField()
    nit_beneficiario = models.BigIntegerField()
    aliado = models.CharField(max_length=255)
    tipo_cta_destino = models.CharField(max_length=50)
    cod_tipo_cuenta_destino = models.IntegerField()
    num_cta_destino = models.BigIntegerField()
    banco_destino = models.CharField(max_length=100)
    cod_banco_destino = models.IntegerField()
    valor_desembolso = models.FloatField()
    numero_tramos = models.IntegerField()
    plazo_tramo_1 = models.IntegerField()
    tipo_tasa_tramo_1 = models.CharField(max_length=10)
    tasa_tramo_1 = models.FloatField()
    amortizacion_tramo_1 = models.CharField(max_length=10)
    plazo_tramo_2 = models.IntegerField()
    tipo_tasa_tramo_2 = models.CharField(max_length=10)
    tasa_tramo_2 = models.FloatField()
    amortizacion_tramo_2 = models.CharField(max_length=10)
    dia_pago_cuota = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Desembolso {self.referencia}"


class CargoFijo(models.Model):
    desembolso = models.ForeignKey(Desembolso, related_name='cargos_fijos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10)
    nombre_cargo_fijo = models.CharField(max_length=255)
    fecha_efectiva = models.DateField(null=True, blank=True)
    fecha_revision = models.DateField(null=True, blank=True)
    periodicidad = models.CharField(max_length=50, null=True, blank=True)
    valor = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_cargo_fijo} ({self.codigo})"
    

class Garantia(models.Model):
    referencia = models.CharField(max_length=100, null=True, blank=True)
    obligacion = models.BigIntegerField()
    id_cliente = models.BigIntegerField()
    id_garante = models.BigIntegerField()
    cod_fasecolda = models.CharField(max_length=50)
    codigo_fasecolda = models.CharField(max_length=50)
    color = models.CharField(max_length=100, null=True, blank=True)
    placa = models.CharField(max_length=20)
    poliza_vehiculo = models.CharField(max_length=50, null=True, blank=True)
    cod_aseguradora = models.CharField(max_length=20, null=True, blank=True)
    nro_poliza = models.CharField(max_length=50, null=True, blank=True)
    valor_asegurado = models.FloatField(null=True, blank=True)
    fecha_vencimiento_seguro = models.DateField(null=True, blank=True)
    tipo_prima = models.CharField(max_length=50, null=True, blank=True)
    valor_prima = models.FloatField(null=True, blank=True)
    folio_electronico = models.CharField(max_length=50, null=True, blank=True)
    valor_vehiculo = models.BigIntegerField(null=True, blank=True)
    modelo = models.CharField(max_length=10, null=True, blank=True)
    fecha_prenda = models.DateField(null=True, blank=True)
    chasis = models.CharField(max_length=50, null=True, blank=True)
    motor = models.CharField(max_length=50, null=True, blank=True)
    serie = models.CharField(max_length=50, null=True, blank=True)
    servicio = models.CharField(max_length=50, null=True, blank=True)
    fecha_desembolso = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Garantía {self.placa} - Referencia {self.referencia}"
