from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import transaction
from .models import (
    Desembolso, CargoFijo, Garantia, EjecucionETL, 
    ProcesoDesembolso, ProcesoGarantia
)
from .forms import DesembolsoForm, CargoFijoFormSet, GarantiaForm

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


# ============================================================================
# VISTAS CRUD PARA DESEMBOLSOS
# ============================================================================

class DesembolsoListView(ListView):
    """Lista de desembolsos con filtros y búsqueda"""
    model = Desembolso
    template_name = 'dexter/desembolso_list.html'
    context_object_name = 'desembolsos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        
        # Filtro por búsqueda
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(referencia__icontains=query) |
                Q(aliado__icontains=query) |
                Q(estado__icontains=query) |
                Q(obligacion__icontains=query)
            )
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['estado_filter'] = self.request.GET.get('estado', '')
        # Obtener estados únicos para el filtro
        context['estados_disponibles'] = Desembolso.objects.values_list('estado', flat=True).distinct().exclude(estado__isnull=True)
        return context


class DesembolsoDetailView(DetailView):
    """Vista detallada de un desembolso con sus cargos fijos"""
    model = Desembolso
    template_name = 'dexter/desembolso_detail.html'
    context_object_name = 'desembolso'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cargos_fijos'] = self.object.cargos_fijos.all()
        return context


class DesembolsoCreateView(CreateView):
    """Vista para crear un nuevo desembolso con cargos fijos"""
    model = Desembolso
    form_class = DesembolsoForm
    template_name = 'dexter/desembolso_form.html'
    success_url = reverse_lazy('dexter:desembolso_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nuevo Desembolso'
        context['es_creacion'] = True
        if self.request.POST:
            context['cargos_formset'] = CargoFijoFormSet(self.request.POST)
        else:
            context['cargos_formset'] = CargoFijoFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        cargos_formset = context['cargos_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if cargos_formset.is_valid():
                cargos_formset.instance = self.object
                cargos_formset.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Desembolso {self.object.referencia} creado exitosamente.')
        return redirect(self.success_url)


class DesembolsoUpdateView(UpdateView):
    """Vista para editar un desembolso existente"""
    model = Desembolso
    form_class = DesembolsoForm
    template_name = 'dexter/desembolso_form.html'
    success_url = reverse_lazy('dexter:desembolso_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Desembolso: {self.object.referencia}'
        context['es_creacion'] = False
        if self.request.POST:
            context['cargos_formset'] = CargoFijoFormSet(self.request.POST, instance=self.object)
        else:
            context['cargos_formset'] = CargoFijoFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        cargos_formset = context['cargos_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if cargos_formset.is_valid():
                cargos_formset.instance = self.object
                cargos_formset.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Desembolso {self.object.referencia} actualizado exitosamente.')
        return redirect(self.success_url)


class DesembolsoDeleteView(DeleteView):
    """Vista para eliminar un desembolso"""
    model = Desembolso
    template_name = 'dexter/desembolso_confirm_delete.html'
    success_url = reverse_lazy('dexter:desembolso_list')
    context_object_name = 'desembolso'
    
    def delete(self, request, *args, **kwargs):
        desembolso = self.get_object()
        messages.success(request, f'Desembolso {desembolso.referencia} eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# VISTAS CRUD PARA GARANTÍAS
# ============================================================================

class GarantiaListView(ListView):
    """Lista de garantías con filtros y búsqueda"""
    model = Garantia
    template_name = 'dexter/garantia_list.html'
    context_object_name = 'garantias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        
        # Filtro por búsqueda
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(placa__icontains=query) |
                Q(referencia__icontains=query) |
                Q(estado__icontains=query) |
                Q(chasis__icontains=query) |
                Q(motor__icontains=query)
            )
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['estado_filter'] = self.request.GET.get('estado', '')
        # Obtener estados únicos para el filtro
        context['estados_disponibles'] = Garantia.objects.values_list('estado', flat=True).distinct().exclude(estado__isnull=True)
        return context


class GarantiaDetailView(DetailView):
    """Vista detallada de una garantía"""
    model = Garantia
    template_name = 'dexter/garantia_detail.html'
    context_object_name = 'garantia'


class GarantiaCreateView(CreateView):
    """Vista para crear una nueva garantía"""
    model = Garantia
    form_class = GarantiaForm
    template_name = 'dexter/garantia_form.html'
    success_url = reverse_lazy('dexter:garantia_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nueva Garantía'
        context['es_creacion'] = True
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f'Garantía {self.object.placa} creada exitosamente.')
        return redirect(self.success_url)


class GarantiaUpdateView(UpdateView):
    """Vista para editar una garantía existente"""
    model = Garantia
    form_class = GarantiaForm
    template_name = 'dexter/garantia_form.html'
    success_url = reverse_lazy('dexter:garantia_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Garantía: {self.object.placa}'
        context['es_creacion'] = False
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f'Garantía {self.object.placa} actualizada exitosamente.')
        return redirect(self.success_url)


class GarantiaDeleteView(DeleteView):
    """Vista para eliminar una garantía"""
    model = Garantia
    template_name = 'dexter/garantia_confirm_delete.html'
    success_url = reverse_lazy('dexter:garantia_list')
    context_object_name = 'garantia'
    
    def delete(self, request, *args, **kwargs):
        garantia = self.get_object()
        messages.success(request, f'Garantía {garantia.placa} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
