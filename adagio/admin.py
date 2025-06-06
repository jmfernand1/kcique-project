from django.contrib import admin
from .models import CasoDebito

@admin.register(CasoDebito)
class CasoDebitoAdmin(admin.ModelAdmin):
    list_display = (
        'cod_caso_bizagi',
        'estado',
        'num_prestamo',
        'tipo_de_cuenta',
        'fecha_creacion',
        'fecha_actualizacion',
        'proceso_creador',
        'proceso_actualizador'
    )
    list_filter = ('estado', 'tipo_de_cuenta', 'fecha_creacion')
    search_fields = ('cod_caso_bizagi', 'num_prestamo', 'numcta_debito')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        (None, {
            'fields': ('cod_caso_bizagi', 'num_prestamo', 'estado')
        }),
        ('Detalles de Cuenta', {
            'fields': ('docsoldv', 'tipo_de_cuenta', 'numcta_debito', 'secuencia_cta', 'codigo_del_banco', 'codigo_ciudad')
        }),
        ('Trazabilidad', {
            'fields': (
                'fecha_creacion', 
                'fecha_actualizacion', 
                'fecha_inicio_proceso', 
                'fecha_fin_proceso', 
                'intentos_procesamiento', 
                'ultimo_error',
                'datos_adicionales'
            )
        }),
        ('Procesos Externos', {
            'fields': ('proceso_creador', 'proceso_actualizador')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # Cuando se edita un objeto existente
            return self.readonly_fields + ('cod_caso_bizagi', 'proceso_creador')
        return self.readonly_fields
