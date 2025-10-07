from django.shortcuts import render
from django.utils import timezone
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
