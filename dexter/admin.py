from django.contrib import admin
from .models import Desembolso, CargoFijo, Garantia, EjecucionETL, ProcesoDesembolso, ProcesoGarantia


# ============================================================================
# ADMIN DE DATOS PRINCIPALES
# ============================================================================

class CargoFijoInline(admin.TabularInline):
    """Inline para mostrar cargos fijos dentro del admin de Desembolso"""
    model = CargoFijo
    extra = 1
    fields = ['codigo', 'nombre_cargo_fijo', 'fecha_efectiva', 'periodicidad', 'valor']


@admin.register(Desembolso)
class DesembolsoAdmin(admin.ModelAdmin):
    """Administrador para el modelo Desembolso"""
    list_display = [
        'referencia', 'obligacion', 'id_cliente', 'aliado', 
        'valor_desembolso', 'banco_destino', 'numero_tramos'
    ]
    list_filter = ['aliado', 'banco_destino', 'tipo_cta_destino', 'numero_tramos']
    search_fields = ['referencia', 'obligacion', 'id_cliente', 'nit_beneficiario', 'aliado']
    readonly_fields = ['id']
    inlines = [CargoFijoInline]
    ordering = ['-id']
    
    fieldsets = (
        ('Información General', {
            'fields': ('referencia', 'obligacion', 'id_cliente', 'nit_beneficiario', 'aliado')
        }),
        ('Cuenta Destino', {
            'fields': (
                'tipo_cta_destino', 'cod_tipo_cuenta_destino', 'num_cta_destino', 
                'banco_destino', 'cod_banco_destino'
            )
        }),
        ('Desembolso', {
            'fields': ('valor_desembolso', 'numero_tramos', 'dia_pago_cuota')
        }),
        ('Tramo 1', {
            'fields': ('plazo_tramo_1', 'tipo_tasa_tramo_1', 'tasa_tramo_1', 'amortizacion_tramo_1'),
            'classes': ('collapse',)
        }),
        ('Tramo 2', {
            'fields': ('plazo_tramo_2', 'tipo_tasa_tramo_2', 'tasa_tramo_2', 'amortizacion_tramo_2'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CargoFijo)
class CargoFijoAdmin(admin.ModelAdmin):
    """Administrador para el modelo CargoFijo"""
    list_display = [
        'nombre_cargo_fijo', 'codigo', 'desembolso', 
        'fecha_efectiva', 'periodicidad', 'valor'
    ]
    list_filter = ['periodicidad', 'fecha_efectiva']
    search_fields = ['nombre_cargo_fijo', 'codigo', 'desembolso__referencia']
    autocomplete_fields = ['desembolso']
    readonly_fields = ['id']


@admin.register(Garantia)
class GarantiaAdmin(admin.ModelAdmin):
    """Administrador para el modelo Garantia"""
    list_display = [
        'placa', 'referencia', 'obligacion', 'id_cliente', 
        'modelo', 'color', 'valor_vehiculo', 'fecha_desembolso'
    ]
    list_filter = ['servicio', 'fecha_desembolso', 'fecha_vencimiento_seguro']
    search_fields = [
        'referencia', 'placa', 'obligacion', 'id_cliente', 
        'chasis', 'motor', 'nro_poliza', 'folio_electronico'
    ]
    readonly_fields = ['id']
    
    fieldsets = (
        ('Información General', {
            'fields': ('referencia', 'obligacion', 'id_cliente', 'id_garante')
        }),
        ('Vehículo', {
            'fields': (
                'cod_fasecolda', 'codigo_fasecolda', 'placa', 'color', 
                'modelo', 'chasis', 'motor', 'serie', 'servicio', 'valor_vehiculo'
            )
        }),
        ('Seguro', {
            'fields': (
                'poliza_vehiculo', 'cod_aseguradora', 'nro_poliza', 
                'valor_asegurado', 'fecha_vencimiento_seguro', 'tipo_prima', 'valor_prima'
            ),
            'classes': ('collapse',)
        }),
        ('Otros Datos', {
            'fields': ('folio_electronico', 'fecha_prenda', 'fecha_desembolso'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# ADMIN DE TRACKING ETL
# ============================================================================

@admin.register(EjecucionETL)
class EjecucionETLAdmin(admin.ModelAdmin):
    """Administrador para EjecucionETL"""
    list_display = [
        'id', 'tipo_proceso', 'estado', 'fecha_inicio', 
        'registros_procesados', 'total_registros', 'mostrar_progreso'
    ]
    list_filter = ['tipo_proceso', 'estado', 'fecha_inicio']
    search_fields = ['descripcion']
    readonly_fields = ['fecha_inicio', 'fecha_fin']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información General', {
            'fields': ('tipo_proceso', 'estado', 'descripcion')
        }),
        ('Estadísticas', {
            'fields': (
                'total_registros', 'registros_procesados', 
                'registros_exitosos', 'registros_fallidos'
            )
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Errores', {
            'fields': ('ultima_etapa_ejecutada', 'mensaje_error'),
            'classes': ('collapse',)
        }),
    )
    
    def mostrar_progreso(self, obj):
        """Muestra el progreso en porcentaje"""
        if obj.total_registros == 0:
            return "0%"
        progreso = (obj.registros_procesados / obj.total_registros) * 100
        return f"{progreso:.1f}%"
    mostrar_progreso.short_description = 'Progreso'


@admin.register(ProcesoDesembolso)
class ProcesoDesembolsoAdmin(admin.ModelAdmin):
    """Administrador para ProcesoDesembolso"""
    list_display = [
        'id', 'desembolso', 'ejecucion', 'etapa_actual', 
        'intentos', 'fecha_ultima_actualizacion'
    ]
    list_filter = ['etapa_actual', 'ejecucion']
    search_fields = ['desembolso__referencia']
    readonly_fields = ['fecha_inicio', 'fecha_ultima_actualizacion', 'fecha_completado']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información', {
            'fields': ('ejecucion', 'desembolso', 'etapa_actual')
        }),
        ('Estado', {
            'fields': ('intentos', 'mensaje_error')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_ultima_actualizacion', 'fecha_completado')
        }),
        ('Datos de Etapa', {
            'fields': ('datos_etapa',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcesoGarantia)
class ProcesoGarantiaAdmin(admin.ModelAdmin):
    """Administrador para ProcesoGarantia"""
    list_display = [
        'id', 'garantia', 'ejecucion', 'etapa_actual', 
        'intentos', 'fecha_ultima_actualizacion'
    ]
    list_filter = ['etapa_actual', 'ejecucion']
    search_fields = ['garantia__placa', 'garantia__referencia']
    readonly_fields = ['fecha_inicio', 'fecha_ultima_actualizacion', 'fecha_completado']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información', {
            'fields': ('ejecucion', 'garantia', 'etapa_actual')
        }),
        ('Estado', {
            'fields': ('intentos', 'mensaje_error')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_ultima_actualizacion', 'fecha_completado')
        }),
        ('Datos de Etapa', {
            'fields': ('datos_etapa',),
            'classes': ('collapse',)
        }),
    )
