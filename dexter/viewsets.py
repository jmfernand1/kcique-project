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
from .models import (
    Desembolso, CargoFijo, Garantia, EjecucionETL, 
    ProcesoDesembolso, ProcesoGarantia,
    EtapaProcesoDesembolso, EtapaProcesoGarantia,
    EtapaTipoDesembolso, EtapaTipoGarantia,
    TipoDesembolso, TipoGarantia
)
from .services import (
    EjecucionETLService,
    ProcesoDesembolsoService,
    ProcesoGarantiaService
)
from .serializers import (
    DesembolsoSerializer, 
    DesembolsoWriteSerializer,
    CargoFijoSerializer, 
    GarantiaSerializer,
    EjecucionETLSerializer,
    ProcesoDesembolsoSerializer,
    ProcesoGarantiaSerializer,
    EtapaProcesoDesembolsoSerializer,
    EtapaProcesoGarantiaSerializer,
    TipoDesembolsoSerializer,
    TipoGarantiaSerializer,
    EtapaTipoDesembolsoSerializer,
    EtapaTipoGarantiaSerializer
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
    
    @action(detail=False, methods=['post'])
    def crear_con_plan(self, request):
        """
        Crea una ejecución con su plan completo.
        
        Body:
        {
            "tipo_proceso": "DESEMBOLSO",
            "total_registros": 100,
            "descripcion": "ETL de prueba",
            "desembolso_ids": [1, 2, 3, ...]  // si tipo_proceso='DESEMBOLSO'
            "garantia_ids": [1, 2, 3, ...]   // si tipo_proceso='GARANTIA'
        }
        """
        tipo_proceso = request.data.get('tipo_proceso')
        total_registros = request.data.get('total_registros')
        descripcion = request.data.get('descripcion')
        
        try:
            if tipo_proceso == 'DESEMBOLSO':
                desembolso_ids = request.data.get('desembolso_ids', [])
                desembolsos = Desembolso.objects.filter(id__in=desembolso_ids)
                ejecucion = EjecucionETLService.crear_ejecucion_con_plan(
                    tipo_proceso=tipo_proceso,
                    total_registros=total_registros,
                    descripcion=descripcion,
                    desembolsos=list(desembolsos)
                )
            elif tipo_proceso == 'GARANTIA':
                garantia_ids = request.data.get('garantia_ids', [])
                garantias = Garantia.objects.filter(id__in=garantia_ids)
                ejecucion = EjecucionETLService.crear_ejecucion_con_plan(
                    tipo_proceso=tipo_proceso,
                    total_registros=total_registros,
                    descripcion=descripcion,
                    garantias=list(garantias)
                )
            else:
                return Response(
                    {'error': 'tipo_proceso debe ser DESEMBOLSO o GARANTIA'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = EjecucionETLSerializer(ejecucion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtiene ejecuciones que no están completadas"""
        tipo_proceso = request.query_params.get('tipo_proceso')
        ejecuciones = EjecucionETLService.obtener_ejecuciones_pendientes(tipo_proceso)
        serializer = self.get_serializer(ejecuciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retomar(self, request, pk=None):
        """Retoma una ejecución pausada o fallida"""
        try:
            ejecucion = EjecucionETLService.retomar_ejecucion(int(pk))
            serializer = self.get_serializer(ejecucion)
            return Response(serializer.data)
        except EjecucionETL.DoesNotExist:
            return Response(
                {'error': 'Ejecución no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marca una ejecución como completada"""
        try:
            ejecucion = EjecucionETLService.completar_ejecucion(int(pk))
            serializer = self.get_serializer(ejecucion)
            return Response(serializer.data)
        except EjecucionETL.DoesNotExist:
            return Response(
                {'error': 'Ejecución no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def fallar(self, request, pk=None):
        """Marca una ejecución como fallida"""
        try:
            mensaje_error = request.data.get('mensaje_error')
            ejecucion = EjecucionETLService.fallar_ejecucion(int(pk), mensaje_error)
            serializer = self.get_serializer(ejecucion)
            return Response(serializer.data)
        except EjecucionETL.DoesNotExist:
            return Response(
                {'error': 'Ejecución no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def progreso(self, request, pk=None):
        """Obtiene el progreso detallado de una ejecución"""
        ejecucion = self.get_object()
        
        from django.db.models import Count
        if ejecucion.tipo_proceso == 'DESEMBOLSO':
            # Contar etapas por estado
            etapas_count = {}
            etapas_agrupadas = EtapaProcesoDesembolso.objects.filter(
                proceso__ejecucion=ejecucion
            ).values('etapa__nombre', 'estado').annotate(count=Count('id'))
            for item in etapas_agrupadas:
                key = f"{item['etapa__nombre']} ({item['estado']})"
                etapas_count[key] = item['count']
        else:
            etapas_count = {}
            etapas_agrupadas = EtapaProcesoGarantia.objects.filter(
                proceso__ejecucion=ejecucion
            ).values('etapa__nombre', 'estado').annotate(count=Count('id'))
            for item in etapas_agrupadas:
                key = f"{item['etapa__nombre']} ({item['estado']})"
                etapas_count[key] = item['count']
        
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
    - GET /api/procesos-desembolso/{id}/ - Obtener proceso
    - GET /api/procesos-desembolso/{id}/siguiente_etapa/ - Obtener siguiente etapa
    """
    queryset = ProcesoDesembolso.objects.all().select_related('desembolso', 'ejecucion').prefetch_related('etapas__etapa')
    serializer_class = ProcesoDesembolsoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ejecucion', 'estado_general', 'desembolso']
    ordering = ['fecha_creacion']
    
    @action(detail=True, methods=['get'])
    def siguiente_etapa(self, request, pk=None):
        """Obtiene la siguiente etapa pendiente del proceso"""
        try:
            etapa = ProcesoDesembolsoService.obtener_siguiente_etapa(int(pk))
            if etapa:
                serializer = EtapaProcesoDesembolsoSerializer(etapa)
                return Response(serializer.data)
            return Response(
                {'message': 'No hay etapas pendientes'},
                status=status.HTTP_204_NO_CONTENT
            )
        except ProcesoDesembolso.DoesNotExist:
            return Response(
                {'error': 'Proceso no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProcesoGarantiaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar procesos de garantía.
    Similar a ProcesoDesembolsoViewSet pero para garantías.
    """
    queryset = ProcesoGarantia.objects.all().select_related('garantia', 'ejecucion').prefetch_related('etapas__etapa')
    serializer_class = ProcesoGarantiaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ejecucion', 'estado_general', 'garantia']
    ordering = ['-fecha_creacion']
    
    @action(detail=True, methods=['get'])
    def siguiente_etapa(self, request, pk=None):
        """Obtiene la siguiente etapa pendiente del proceso"""
        try:
            etapa = ProcesoGarantiaService.obtener_siguiente_etapa(int(pk))
            if etapa:
                serializer = EtapaProcesoGarantiaSerializer(etapa)
                return Response(serializer.data)
            return Response(
                {'message': 'No hay etapas pendientes'},
                status=status.HTTP_204_NO_CONTENT
            )
        except ProcesoGarantia.DoesNotExist:
            return Response(
                {'error': 'Proceso no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

class TipoDesembolsoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar tipos de desembolso.
    Endpoints:
    - GET /api/tipos-desembolso/ - Listar tipos de desembolso
    - GET /api/tipos-desembolso/{id}/ - Obtener un tipo de desembolso
    - GET /api/tipos-desembolso/{id}/etapas/ - Obtener las etapas de un tipo de desembolso
    """
    queryset = TipoDesembolso.objects.all().prefetch_related('etapas')
    serializer_class = TipoDesembolsoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nombre']
    ordering = ['-id']

    @action(detail=True, methods=['get'])
    def etapas(self, request, pk=None):
        """Obtiene las etapas de un tipo de desembolso"""
        tipo_desembolso = self.get_object()
        etapas = EtapaTipoDesembolso.objects.filter(tipo_desembolso=tipo_desembolso)
        serializer = EtapaTipoDesembolsoSerializer(etapas, many=True)
        return Response(serializer.data)

class TipoGarantiaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar tipos de garantía.
    """
    queryset = TipoGarantia.objects.all()
    serializer_class = TipoGarantiaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nombre']
    ordering = ['-id']

class EtapaTipoDesembolsoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar etapas de tipo de desembolso.
    """
    queryset = EtapaTipoDesembolso.objects.all()
    serializer_class = EtapaTipoDesembolsoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nombre']
    ordering = ['-id']

class EtapaTipoGarantiaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar etapas de tipo de garantía.
    """
    queryset = EtapaTipoGarantia.objects.all()
    serializer_class = EtapaTipoGarantiaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nombre']
    ordering = ['-id']


class EtapaProcesoDesembolsoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar etapas individuales de procesos de desembolso.
    
    Endpoints:
    - GET /api/etapas-proceso-desembolso/ - Listar etapas
    - GET /api/etapas-proceso-desembolso/{id}/ - Obtener etapa
    - POST /api/etapas-proceso-desembolso/{id}/iniciar/ - Iniciar etapa
    - POST /api/etapas-proceso-desembolso/{id}/completar/ - Completar etapa
    - POST /api/etapas-proceso-desembolso/{id}/marcar_error/ - Marcar error
    - POST /api/etapas-proceso-desembolso/{id}/reintentar/ - Reintentar etapa
    """
    queryset = EtapaProcesoDesembolso.objects.all().select_related('proceso', 'etapa')
    serializer_class = EtapaProcesoDesembolsoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['proceso', 'etapa', 'estado']
    ordering = ['orden']
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Inicia una etapa"""
        try:
            etapa = ProcesoDesembolsoService.iniciar_etapa(int(pk))
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoDesembolso.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completa una etapa"""
        datos_etapa = request.data.get('datos_etapa')
        try:
            etapa = ProcesoDesembolsoService.completar_etapa(
                int(pk),
                datos_etapa=datos_etapa
            )
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoDesembolso.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def marcar_error(self, request, pk=None):
        """Marca una etapa como error"""
        mensaje_error = request.data.get('mensaje_error', '')
        datos_etapa = request.data.get('datos_etapa')
        try:
            etapa = ProcesoDesembolsoService.marcar_error_etapa(
                int(pk),
                mensaje_error,
                datos_etapa=datos_etapa
            )
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoDesembolso.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reintentar(self, request, pk=None):
        """Reintenta una etapa que falló"""
        try:
            etapa = ProcesoDesembolsoService.reintentar_etapa(int(pk))
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoDesembolso.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EtapaProcesoGarantiaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar etapas individuales de procesos de garantía.
    
    Endpoints:
    - GET /api/etapas-proceso-garantia/ - Listar etapas
    - GET /api/etapas-proceso-garantia/{id}/ - Obtener etapa
    - POST /api/etapas-proceso-garantia/{id}/iniciar/ - Iniciar etapa
    - POST /api/etapas-proceso-garantia/{id}/completar/ - Completar etapa
    - POST /api/etapas-proceso-garantia/{id}/marcar_error/ - Marcar error
    - POST /api/etapas-proceso-garantia/{id}/reintentar/ - Reintentar etapa
    """
    queryset = EtapaProcesoGarantia.objects.all().select_related('proceso', 'etapa')
    serializer_class = EtapaProcesoGarantiaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['proceso', 'etapa', 'estado']
    ordering = ['orden']
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Inicia una etapa"""
        try:
            etapa = ProcesoGarantiaService.iniciar_etapa(int(pk))
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoGarantia.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completa una etapa"""
        datos_etapa = request.data.get('datos_etapa')
        try:
            etapa = ProcesoGarantiaService.completar_etapa(
                int(pk),
                datos_etapa=datos_etapa
            )
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoGarantia.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def marcar_error(self, request, pk=None):
        """Marca una etapa como error"""
        mensaje_error = request.data.get('mensaje_error', '')
        datos_etapa = request.data.get('datos_etapa')
        try:
            etapa = ProcesoGarantiaService.marcar_error_etapa(
                int(pk),
                mensaje_error,
                datos_etapa=datos_etapa
            )
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoGarantia.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reintentar(self, request, pk=None):
        """Reintenta una etapa que falló"""
        try:
            etapa = ProcesoGarantiaService.reintentar_etapa(int(pk))
            serializer = self.get_serializer(etapa)
            return Response(serializer.data)
        except EtapaProcesoGarantia.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )