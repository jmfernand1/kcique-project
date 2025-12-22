from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from .models import (
    Desembolso, CargoFijo, Garantia, EjecucionETL, 
    ProcesoDesembolso, ProcesoGarantia
)

# ============================================================================
# VISTAS HTML PARA FRONTEND
# ============================================================================

def dashboard_dexter(request):
    """Dashboard principal de Dexter con estadísticas de ejecuciones ETL"""
    
    # Estadísticas de ejecuciones
    total_ejecuciones = EjecucionETL.objects.count()
    ejecuciones_iniciadas = EjecucionETL.objects.filter(estado='INICIADO').count()
    ejecuciones_en_progreso = EjecucionETL.objects.filter(estado='EN_PROGRESO').count()
    ejecuciones_completadas = EjecucionETL.objects.filter(estado='COMPLETADO').count()
    ejecuciones_fallidas = EjecucionETL.objects.filter(estado='FALLIDO').count()
    ejecuciones_pausadas = EjecucionETL.objects.filter(estado='PAUSADO').count()
    
    # Estadísticas por tipo de proceso
    total_desembolsos = EjecucionETL.objects.filter(tipo_proceso='DESEMBOLSO').count()
    total_garantias = EjecucionETL.objects.filter(tipo_proceso='GARANTIA').count()
    
    # Promedio de tiempo de ejecución para ejecuciones completadas
    ejecuciones_completadas_con_tiempo = EjecucionETL.objects.filter(
        estado='COMPLETADO',
        fecha_inicio__isnull=False,
        fecha_fin__isnull=False
    ).annotate(
        tiempo_ejecucion=ExpressionWrapper(
            F('fecha_fin') - F('fecha_inicio'), 
            output_field=DurationField()
        )
    )
    
    promedio_ejecucion_data = ejecuciones_completadas_con_tiempo.aggregate(Avg('tiempo_ejecucion'))
    promedio_ejecucion = promedio_ejecucion_data['tiempo_ejecucion__avg']
    
    # Ejecuciones recientes
    ejecuciones_recientes = EjecucionETL.objects.all().order_by('-fecha_inicio')[:10]
    
    context = {
        'total_ejecuciones': total_ejecuciones,
        'ejecuciones_iniciadas': ejecuciones_iniciadas,
        'ejecuciones_en_progreso': ejecuciones_en_progreso,
        'ejecuciones_completadas': ejecuciones_completadas,
        'ejecuciones_fallidas': ejecuciones_fallidas,
        'ejecuciones_pausadas': ejecuciones_pausadas,
        'total_desembolsos': total_desembolsos,
        'total_garantias': total_garantias,
        'promedio_ejecucion': promedio_ejecucion,
        'ejecuciones_recientes': ejecuciones_recientes,
    }
    
    return render(request, 'dexter/dashboard.html', context)


class EjecucionETLListView(ListView):
    """Lista de ejecuciones ETL con filtros y búsqueda"""
    model = EjecucionETL
    template_name = 'dexter/ejecucion_list.html'
    context_object_name = 'ejecuciones'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-fecha_inicio')
        
        # Filtro por búsqueda
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(tipo_proceso__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(estado__icontains=query)
            )
        
        # Filtro por tipo de proceso
        tipo_proceso = self.request.GET.get('tipo_proceso')
        if tipo_proceso:
            queryset = queryset.filter(tipo_proceso=tipo_proceso)
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['tipo_proceso_filter'] = self.request.GET.get('tipo_proceso', '')
        context['estado_filter'] = self.request.GET.get('estado', '')
        context['tipo_proceso_choices'] = EjecucionETL.TIPO_CHOICES
        context['estado_choices'] = EjecucionETL.ESTADO_CHOICES
        return context


class EjecucionETLDetailView(DetailView):
    """Vista detallada de una ejecución ETL con todos sus procesos y etapas"""
    model = EjecucionETL
    template_name = 'dexter/ejecucion_detail.html'
    context_object_name = 'ejecucion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ejecucion = self.object
        
        # Obtener procesos según el tipo
        if ejecucion.tipo_proceso == 'DESEMBOLSO':
            procesos = ProcesoDesembolso.objects.filter(
                ejecucion=ejecucion
            ).select_related('desembolso', 'etapa').order_by('-fecha_creacion')
            
            # Estadísticas por etapa
            from django.db.models import Count
            etapas_stats = {}
            etapas_agrupadas = procesos.values('etapa__nombre', 'etapa__id').annotate(count=Count('id'))
            for item in etapas_agrupadas:
                etapas_stats[item['etapa__nombre']] = {
                    'count': item['count'],
                    'code': item['etapa__id']
                }
            
            context['procesos'] = procesos
            context['etapas_stats'] = etapas_stats
            context['tipo_proceso'] = 'DESEMBOLSO'
            
        else:  # GARANTIA
            procesos = ProcesoGarantia.objects.filter(
                ejecucion=ejecucion
            ).select_related('garantia', 'etapa').order_by('-fecha_creacion')
            
            # Estadísticas por etapa
            from django.db.models import Count
            etapas_stats = {}
            etapas_agrupadas = procesos.values('etapa__nombre', 'etapa__id').annotate(count=Count('id'))
            for item in etapas_agrupadas:
                etapas_stats[item['etapa__nombre']] = {
                    'count': item['count'],
                    'code': item['etapa__id']
                }
            
            context['procesos'] = procesos
            context['etapas_stats'] = etapas_stats
            context['tipo_proceso'] = 'GARANTIA'
        
        # Calcular progreso
        if ejecucion.total_registros > 0:
            progreso_porcentaje = round(
                (ejecucion.registros_procesados / ejecucion.total_registros) * 100, 2
            )
        else:
            progreso_porcentaje = 0
        
        context['progreso_porcentaje'] = progreso_porcentaje
        
        return context
