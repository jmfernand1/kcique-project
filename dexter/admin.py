from django.contrib import admin
from .models import Desembolso, CargoFijo, Garantia


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
    # Necesario para que funcione autocomplete_fields en otros modelos
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
