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

class TipoDesembolso(models.Model):
    """Tipo de desembolso"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Desembolso"
        verbose_name_plural = "Tipos de Desembolso"

class EtapaTipoDesembolso(models.Model):
    """Etapa de tipo de desembolso"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    orden = models.IntegerField()
    tipo_desembolso = models.ForeignKey(TipoDesembolso, on_delete=models.CASCADE, related_name='etapas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Etapa de Tipo de Desembolso"
        verbose_name_plural = "Etapas de Tipo de Desembolso"
        ordering = ['orden']


class ProcesoDesembolso(models.Model):
    """
    Contenedor principal del proceso de un desembolso.
    Agrupa todas las etapas que debe completar.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
        ('PAUSADO', 'Pausado'),
    ]
    
    ejecucion = models.ForeignKey(EjecucionETL, on_delete=models.CASCADE, related_name='procesos_desembolso')
    desembolso = models.ForeignKey('Desembolso', on_delete=models.CASCADE, related_name='procesos_etl')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    estado_general = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Proceso de Desembolso"
        verbose_name_plural = "Procesos de Desembolso"
    
    def __str__(self):
        return f"Desembolso {self.desembolso.referencia}"
    
    @property
    def etapa_actual(self):
        """Retorna la etapa actual (primera pendiente o en progreso)"""
        return self.etapas.filter(
            estado__in=['PENDIENTE', 'EN_PROGRESO']
        ).order_by('orden').first()
    
    @property
    def siguiente_etapa(self):
        """Retorna la siguiente etapa pendiente"""
        return self.etapas.filter(estado='PENDIENTE').order_by('orden').first()
    
    def avanzar_a_siguiente_etapa(self):
        """Avanza automáticamente a la siguiente etapa pendiente"""
        etapa_actual = self.etapa_actual
        if etapa_actual and etapa_actual.estado == 'COMPLETADO':
            siguiente = self.siguiente_etapa
            if siguiente:
                siguiente.estado = 'EN_PROGRESO'
                siguiente.save()
                self.estado_general = 'EN_PROGRESO'
                self.save()
        return self.etapa_actual
    
    def marcar_como_completado(self):
        """Marca el proceso como completado si todas las etapas están completadas"""
        if self.etapas.filter(estado__in=['PENDIENTE', 'EN_PROGRESO', 'ERROR']).exists():
            return False
        self.estado_general = 'COMPLETADO'
        self.fecha_completado = timezone.now()
        self.save()
        return True


class EtapaProcesoDesembolso(models.Model):
    """
    Representa una etapa individual del proceso de desembolso.
    Cada ProcesoDesembolso tiene múltiples EtapaProcesoDesembolso.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
        ('OMITIDA', 'Omitida'),
    ]
    
    proceso = models.ForeignKey(
        ProcesoDesembolso, 
        on_delete=models.CASCADE, 
        related_name='etapas'
    )
    etapa = models.ForeignKey(
        EtapaTipoDesembolso, 
        on_delete=models.CASCADE, 
        related_name='procesos_etapas'
    )
    orden = models.IntegerField(help_text="Orden de ejecución de la etapa")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    intentos = models.IntegerField(default=0)
    mensaje_error = models.TextField(null=True, blank=True)
    datos_etapa = models.JSONField(null=True, blank=True, default=dict)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Etapa de Proceso Desembolso"
        verbose_name_plural = "Etapas de Proceso Desembolso"
        unique_together = [['proceso', 'etapa']]
    
    def __str__(self):
        return f"{self.proceso.desembolso.referencia} - {self.etapa.nombre} ({self.estado})"
    
    def iniciar(self):
        """Marca la etapa como en progreso"""
        self.estado = 'EN_PROGRESO'
        self.fecha_inicio = timezone.now()
        self.intentos += 1
        self.save()
    
    def completar(self, datos_etapa=None):
        """Marca la etapa como completada"""
        self.estado = 'COMPLETADO'
        self.fecha_completado = timezone.now()
        if datos_etapa:
            if not self.datos_etapa:
                self.datos_etapa = {}
            self.datos_etapa.update(datos_etapa)
        self.save()
        # Avanzar al siguiente si es necesario
        self.proceso.avanzar_a_siguiente_etapa()
        self.proceso.marcar_como_completado()
    
    def marcar_error(self, mensaje_error, datos_etapa=None):
        """Marca la etapa como error"""
        self.estado = 'ERROR'
        self.mensaje_error = mensaje_error
        self.intentos += 1
        if datos_etapa:
            if not self.datos_etapa:
                self.datos_etapa = {}
            self.datos_etapa.update(datos_etapa)
        self.save()
        self.proceso.estado_general = 'ERROR'
        self.proceso.save()

class TipoGarantia(models.Model):
    """Tipo de garantía"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Garantía"
        verbose_name_plural = "Tipos de Garantía"

class EtapaTipoGarantia(models.Model):
    """Etapa de tipo de garantía"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    orden = models.IntegerField()
    tipo_garantia = models.ForeignKey(TipoGarantia, on_delete=models.CASCADE, related_name='etapas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Etapa de Tipo de Garantía"
        verbose_name_plural = "Etapas de Tipo de Garantía"
        ordering = ['orden']

class ProcesoGarantia(models.Model):
    """
    Contenedor principal del proceso de una garantía.
    Agrupa todas las etapas que debe completar.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
        ('PAUSADO', 'Pausado'),
    ]
    
    ejecucion = models.ForeignKey(EjecucionETL, on_delete=models.CASCADE, related_name='procesos_garantia')
    garantia = models.ForeignKey('Garantia', on_delete=models.CASCADE, related_name='procesos_etl')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    estado_general = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Proceso de Garantía"
        verbose_name_plural = "Procesos de Garantía"
    
    def __str__(self):
        return f"Garantía {self.garantia.placa}"
    
    @property
    def etapa_actual(self):
        """Retorna la etapa actual (primera pendiente o en progreso)"""
        return self.etapas.filter(
            estado__in=['PENDIENTE', 'EN_PROGRESO']
        ).order_by('orden').first()
    
    @property
    def siguiente_etapa(self):
        """Retorna la siguiente etapa pendiente"""
        return self.etapas.filter(estado='PENDIENTE').order_by('orden').first()
    
    def avanzar_a_siguiente_etapa(self):
        """Avanza automáticamente a la siguiente etapa pendiente"""
        etapa_actual = self.etapa_actual
        if etapa_actual and etapa_actual.estado == 'COMPLETADO':
            siguiente = self.siguiente_etapa
            if siguiente:
                siguiente.estado = 'EN_PROGRESO'
                siguiente.save()
                self.estado_general = 'EN_PROGRESO'
                self.save()
        return self.etapa_actual
    
    def marcar_como_completado(self):
        """Marca el proceso como completado si todas las etapas están completadas"""
        if self.etapas.filter(estado__in=['PENDIENTE', 'EN_PROGRESO', 'ERROR']).exists():
            return False
        self.estado_general = 'COMPLETADO'
        self.fecha_completado = timezone.now()
        self.save()
        return True


class EtapaProcesoGarantia(models.Model):
    """
    Representa una etapa individual del proceso de garantía.
    Cada ProcesoGarantia tiene múltiples EtapaProcesoGarantia.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
        ('OMITIDA', 'Omitida'),
    ]
    
    proceso = models.ForeignKey(
        ProcesoGarantia, 
        on_delete=models.CASCADE, 
        related_name='etapas'
    )
    etapa = models.ForeignKey(
        EtapaTipoGarantia, 
        on_delete=models.CASCADE, 
        related_name='procesos_etapas'
    )
    orden = models.IntegerField(help_text="Orden de ejecución de la etapa")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    intentos = models.IntegerField(default=0)
    mensaje_error = models.TextField(null=True, blank=True)
    datos_etapa = models.JSONField(null=True, blank=True, default=dict)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Etapa de Proceso Garantía"
        verbose_name_plural = "Etapas de Proceso Garantía"
        unique_together = [['proceso', 'etapa']]
    
    def __str__(self):
        return f"{self.proceso.garantia.placa} - {self.etapa.nombre} ({self.estado})"
    
    def iniciar(self):
        """Marca la etapa como en progreso"""
        self.estado = 'EN_PROGRESO'
        self.fecha_inicio = timezone.now()
        self.intentos += 1
        self.save()
    
    def completar(self, datos_etapa=None):
        """Marca la etapa como completada"""
        self.estado = 'COMPLETADO'
        self.fecha_completado = timezone.now()
        if datos_etapa:
            if not self.datos_etapa:
                self.datos_etapa = {}
            self.datos_etapa.update(datos_etapa)
        self.save()
        # Avanzar al siguiente si es necesario
        self.proceso.avanzar_a_siguiente_etapa()
        self.proceso.marcar_como_completado()
    
    def marcar_error(self, mensaje_error, datos_etapa=None):
        """Marca la etapa como error"""
        self.estado = 'ERROR'
        self.mensaje_error = mensaje_error
        self.intentos += 1
        if datos_etapa:
            if not self.datos_etapa:
                self.datos_etapa = {}
            self.datos_etapa.update(datos_etapa)
        self.save()
        self.proceso.estado_general = 'ERROR'
        self.proceso.save()


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
    tipo_desembolso = models.ForeignKey(TipoDesembolso, on_delete=models.CASCADE, related_name='desembolsos', null=True, blank=True)

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
