from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Desembolso, CargoFijo, Garantia, EjecucionETL, ProcesoDesembolso, ProcesoGarantia
from .serializers import (
    DesembolsoSerializer, 
    DesembolsoWriteSerializer,
    CargoFijoSerializer, 
    GarantiaSerializer,
    EjecucionETLSerializer,
    ProcesoDesembolsoSerializer,
    ProcesoGarantiaSerializer
)


# ============================================================================
# VIEWSETS DE DATOS PRINCIPALES
# ============================================================================

class DesembolsoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Desembolsos.
    
    Endpoints disponibles:
    - GET /api/desembolsos/ - Listar todos los desembolsos
    - POST /api/desembolsos/ - Crear un nuevo desembolso
    - GET /api/desembolsos/{id}/ - Obtener un desembolso específico
    - PUT /api/desembolsos/{id}/ - Actualizar un desembolso completo
    - PATCH /api/desembolsos/{id}/ - Actualizar parcialmente un desembolso
    - DELETE /api/desembolsos/{id}/ - Eliminar un desembolso
    - GET /api/desembolsos/{id}/cargos_fijos/ - Obtener cargos fijos de un desembolso
    """
    queryset = Desembolso.objects.all().prefetch_related('cargos_fijos')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['referencia', 'obligacion', 'id_cliente', 'nit_beneficiario', 'aliado']
    search_fields = ['referencia', 'aliado', 'banco_destino']
    ordering_fields = ['id', 'referencia', 'valor_desembolso']
    ordering = ['-id']
    
    def get_serializer_class(self):
        """Usa diferentes serializers para lectura y escritura"""
        if self.action in ['list', 'retrieve']:
            return DesembolsoSerializer
        return DesembolsoWriteSerializer
    
    @action(detail=True, methods=['get'])
    def cargos_fijos(self, request, pk=None):
        """Endpoint personalizado para obtener los cargos fijos de un desembolso"""
        desembolso = self.get_object()
        cargos = desembolso.cargos_fijos.all()
        serializer = CargoFijoSerializer(cargos, many=True)
        return Response(serializer.data)


class CargoFijoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Cargos Fijos.
    
    Endpoints disponibles:
    - GET /api/cargos-fijos/ - Listar todos los cargos fijos
    - POST /api/cargos-fijos/ - Crear un nuevo cargo fijo
    - GET /api/cargos-fijos/{id}/ - Obtener un cargo fijo específico
    - PUT /api/cargos-fijos/{id}/ - Actualizar un cargo fijo completo
    - PATCH /api/cargos-fijos/{id}/ - Actualizar parcialmente un cargo fijo
    - DELETE /api/cargos-fijos/{id}/ - Eliminar un cargo fijo
    """
    queryset = CargoFijo.objects.all().select_related('desembolso')
    serializer_class = CargoFijoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['desembolso', 'codigo', 'periodicidad']
    search_fields = ['nombre_cargo_fijo', 'codigo']
    ordering_fields = ['id', 'fecha_efectiva', 'valor']
    ordering = ['-id']


class GarantiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Garantías.
    
    Endpoints disponibles:
    - GET /api/garantias/ - Listar todas las garantías
    - POST /api/garantias/ - Crear una nueva garantía
    - GET /api/garantias/{id}/ - Obtener una garantía específica
    - PUT /api/garantias/{id}/ - Actualizar una garantía completa
    - PATCH /api/garantias/{id}/ - Actualizar parcialmente una garantía
    - DELETE /api/garantias/{id}/ - Eliminar una garantía
    """
    queryset = Garantia.objects.all()
    serializer_class = GarantiaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'referencia', 'obligacion', 'id_cliente', 'id_garante', 
        'placa', 'cod_fasecolda', 'cod_aseguradora'
    ]
    search_fields = ['referencia', 'placa', 'chasis', 'motor', 'nro_poliza']
    ordering_fields = ['id', 'placa', 'fecha_desembolso', 'valor_vehiculo']
    ordering = ['-id']


# ============================================================================
# VIEWSETS DE TRACKING ETL
# ============================================================================

class EjecucionETLViewSet(viewsets.ModelViewSet):
    """
    API para gestionar ejecuciones del ETL.
    
    Endpoints:
    - GET /api/ejecuciones/ - Listar todas las ejecuciones
    - POST /api/ejecuciones/ - Crear nueva ejecución
    - GET /api/ejecuciones/{id}/ - Obtener una ejecución
    - PATCH /api/ejecuciones/{id}/ - Actualizar ejecución
    - GET /api/ejecuciones/pendientes/ - Obtener ejecuciones pendientes
    - POST /api/ejecuciones/{id}/completar/ - Marcar como completada
    - POST /api/ejecuciones/{id}/fallar/ - Marcar como fallida
    - GET /api/ejecuciones/{id}/progreso/ - Obtener progreso detallado
    """
    queryset = EjecucionETL.objects.all()
    serializer_class = EjecucionETLSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tipo_proceso', 'estado']
    ordering = ['-fecha_inicio']
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtiene ejecuciones que no están completadas"""
        pendientes = self.queryset.filter(
            estado__in=['INICIADO', 'EN_PROGRESO', 'PAUSADO', 'FALLIDO']
        )
        tipo = request.query_params.get('tipo_proceso')
        if tipo:
            pendientes = pendientes.filter(tipo_proceso=tipo)
        
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marca una ejecución como completada"""
        ejecucion = self.get_object()
        ejecucion.estado = 'COMPLETADO'
        ejecucion.fecha_fin = timezone.now()
        ejecucion.save()
        
        serializer = self.get_serializer(ejecucion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def fallar(self, request, pk=None):
        """Marca una ejecución como fallida"""
        ejecucion = self.get_object()
        ejecucion.estado = 'FALLIDO'
        ejecucion.fecha_fin = timezone.now()
        if 'mensaje_error' in request.data:
            ejecucion.mensaje_error = request.data['mensaje_error']
        ejecucion.save()
        
        serializer = self.get_serializer(ejecucion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progreso(self, request, pk=None):
        """Obtiene el progreso detallado de una ejecución"""
        ejecucion = self.get_object()
        
        if ejecucion.tipo_proceso == 'DESEMBOLSO':
            procesos = ProcesoDesembolso.objects.filter(ejecucion=ejecucion)
            etapas_count = {}
            for etapa in ProcesoDesembolso.ETAPAS:
                etapas_count[etapa[1]] = procesos.filter(etapa_actual=etapa[0]).count()
        else:
            procesos = ProcesoGarantia.objects.filter(ejecucion=ejecucion)
            etapas_count = {}
            for etapa in ProcesoGarantia.ETAPAS:
                etapas_count[etapa[1]] = procesos.filter(etapa_actual=etapa[0]).count()
        
        return Response({
            'ejecucion_id': ejecucion.id,
            'tipo_proceso': ejecucion.tipo_proceso,
            'estado': ejecucion.estado,
            'total_registros': ejecucion.total_registros,
            'registros_procesados': ejecucion.registros_procesados,
            'registros_exitosos': ejecucion.registros_exitosos,
            'registros_fallidos': ejecucion.registros_fallidos,
            'progreso_porcentaje': round((ejecucion.registros_procesados / ejecucion.total_registros * 100) if ejecucion.total_registros > 0 else 0, 2),
            'distribucion_etapas': etapas_count
        })


class ProcesoDesembolsoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar procesos de desembolso.
    
    Endpoints:
    - GET /api/procesos-desembolso/ - Listar procesos
    - POST /api/procesos-desembolso/ - Crear proceso
    - GET /api/procesos-desembolso/{id}/ - Obtener proceso
    - PATCH /api/procesos-desembolso/{id}/ - Actualizar proceso
    - POST /api/procesos-desembolso/{id}/avanzar_etapa/ - Avanzar a siguiente etapa
    - POST /api/procesos-desembolso/{id}/marcar_error/ - Marcar como error
    - POST /api/procesos-desembolso/{id}/completar/ - Marcar como completado
    """
    queryset = ProcesoDesembolso.objects.all().select_related('desembolso', 'ejecucion')
    serializer_class = ProcesoDesembolsoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ejecucion', 'etapa_actual', 'desembolso']
    ordering = ['-fecha_inicio']
    
    @action(detail=True, methods=['post'])
    def avanzar_etapa(self, request, pk=None):
        """Avanza el proceso a la siguiente etapa"""
        proceso = self.get_object()
        nueva_etapa = request.data.get('etapa')
        datos_etapa = request.data.get('datos_etapa')
        
        if not nueva_etapa:
            return Response(
                {'error': 'Se requiere el campo "etapa"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        proceso.etapa_actual = nueva_etapa
        if datos_etapa:
            if not proceso.datos_etapa:
                proceso.datos_etapa = {}
            proceso.datos_etapa.update(datos_etapa)
        proceso.save()
        
        serializer = self.get_serializer(proceso)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_error(self, request, pk=None):
        """Marca el proceso como error"""
        proceso = self.get_object()
        proceso.etapa_actual = 'ERROR'
        proceso.mensaje_error = request.data.get('mensaje_error', '')
        proceso.intentos += 1
        proceso.save()
        
        # Actualizar contador de la ejecución
        proceso.ejecucion.registros_fallidos += 1
        proceso.ejecucion.save()
        
        serializer = self.get_serializer(proceso)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marca el proceso como completado"""
        proceso = self.get_object()
        proceso.etapa_actual = 'COMPLETADO'
        proceso.fecha_completado = timezone.now()
        proceso.save()
        
        # Actualizar contador de la ejecución
        proceso.ejecucion.registros_procesados += 1
        proceso.ejecucion.registros_exitosos += 1
        proceso.ejecucion.save()
        
        serializer = self.get_serializer(proceso)
        return Response(serializer.data)


class ProcesoGarantiaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar procesos de garantía.
    Similar a ProcesoDesembolsoViewSet pero para garantías.
    """
    queryset = ProcesoGarantia.objects.all().select_related('garantia', 'ejecucion')
    serializer_class = ProcesoGarantiaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ejecucion', 'etapa_actual', 'garantia']
    ordering = ['-fecha_inicio']
    
    @action(detail=True, methods=['post'])
    def avanzar_etapa(self, request, pk=None):
        """Avanza el proceso a la siguiente etapa"""
        proceso = self.get_object()
        nueva_etapa = request.data.get('etapa')
        datos_etapa = request.data.get('datos_etapa')
        
        if not nueva_etapa:
            return Response(
                {'error': 'Se requiere el campo "etapa"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        proceso.etapa_actual = nueva_etapa
        if datos_etapa:
            if not proceso.datos_etapa:
                proceso.datos_etapa = {}
            proceso.datos_etapa.update(datos_etapa)
        proceso.save()
        
        serializer = self.get_serializer(proceso)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_error(self, request, pk=None):
        """Marca el proceso como error"""
        proceso = self.get_object()
        proceso.etapa_actual = 'ERROR'
        proceso.mensaje_error = request.data.get('mensaje_error', '')
        proceso.intentos += 1
        proceso.save()
        
        proceso.ejecucion.registros_fallidos += 1
        proceso.ejecucion.save()
        
        serializer = self.get_serializer(proceso)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marca el proceso como completado"""
        proceso = self.get_object()
        proceso.etapa_actual = 'COMPLETADO'
        proceso.fecha_completado = timezone.now()
        proceso.save()
        
        proceso.ejecucion.registros_procesados += 1
        proceso.ejecucion.registros_exitosos += 1
        proceso.ejecucion.save()
        
        serializer = self.get_serializer(proceso)
        return Response(serializer.data)


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
            ).select_related('desembolso').order_by('-fecha_inicio')
            
            # Estadísticas por etapa
            etapas_stats = {}
            for etapa_code, etapa_nombre in ProcesoDesembolso.ETAPAS:
                count = procesos.filter(etapa_actual=etapa_code).count()
                etapas_stats[etapa_nombre] = {
                    'count': count,
                    'code': etapa_code
                }
            
            context['procesos'] = procesos
            context['etapas_stats'] = etapas_stats
            context['tipo_proceso'] = 'DESEMBOLSO'
            
        else:  # GARANTIA
            procesos = ProcesoGarantia.objects.filter(
                ejecucion=ejecucion
            ).select_related('garantia').order_by('-fecha_inicio')
            
            # Estadísticas por etapa
            etapas_stats = {}
            for etapa_code, etapa_nombre in ProcesoGarantia.ETAPAS:
                count = procesos.filter(etapa_actual=etapa_code).count()
                etapas_stats[etapa_nombre] = {
                    'count': count,
                    'code': etapa_code
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
