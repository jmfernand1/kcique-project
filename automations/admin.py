from django.contrib import admin
from .models import AutomatedProcess, ProcessLog, ScheduledTask

@admin.register(AutomatedProcess)
class AutomatedProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_running', 'running_started_at', 'last_run_time', 'last_run_status', 'script_path')
    list_filter = ('is_active', 'is_running', 'last_run_status')
    search_fields = ('name', 'description', 'script_path')
    readonly_fields = ('last_run_time', 'last_run_status', 'created_at', 'updated_at')
    actions = ['liberar_lock_ejecucion']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Configuración Técnica', {
            'fields': ('script_path', 'virtual_env_path')
        }),
        ('Estado de Ejecución', {
            'fields': ('is_running', 'running_started_at'),
            'description': 'Lock a nivel de base de datos. Si un proceso quedó marcado como running tras un crash, usa la acción "Liberar lock" para destrabarlo.'
        }),
        ('Estado y Trazabilidad', {
            'classes': ('collapse',),
            'fields': ('last_run_time', 'last_run_status', 'created_at', 'updated_at')
        }),
    )

    def liberar_lock_ejecucion(self, request, queryset):
        """Acción del admin para liberar manualmente el lock de procesos seleccionados."""
        count = queryset.update(is_running=False, running_started_at=None)
        self.message_user(request, f"Lock liberado para {count} proceso(s).")
    liberar_lock_ejecucion.short_description = "Liberar lock de ejecución (forzar)"

class ScheduledTaskInline(admin.TabularInline):
    model = ScheduledTask
    extra = 0
    fields = ('get_resumen_programacion', 'activo')
    readonly_fields = ('get_resumen_programacion',)

@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ('process', 'get_resumen_programacion', 'activo')
    list_filter = ('activo', 'frecuencia', 'process')
    search_fields = ('process__name',)
    autocomplete_fields = ('process',)

@admin.register(ProcessLog)
class ProcessLogAdmin(admin.ModelAdmin):
    list_display = ('process', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'process')
    search_fields = ('process__name', 'output_log')
    readonly_fields = ('process', 'start_time', 'end_time', 'status', 'output_log')
