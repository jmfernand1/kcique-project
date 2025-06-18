from django.contrib import admin
from .models import AutomatedProcess, ProcessLog, ScheduledTask

@admin.register(AutomatedProcess)
class AutomatedProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'last_run_time', 'last_run_status', 'script_path')
    list_filter = ('is_active', 'last_run_status')
    search_fields = ('name', 'description', 'script_path')
    readonly_fields = ('last_run_time', 'last_run_status', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Configuración Técnica', {
            'fields': ('script_path', 'virtual_env_path')
        }),
        ('Estado y Trazabilidad', {
            'classes': ('collapse',),
            'fields': ('last_run_time', 'last_run_status', 'created_at', 'updated_at')
        }),
    )

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
