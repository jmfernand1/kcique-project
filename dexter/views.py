from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Desembolso, CargoFijo, Garantia
from .serializers import (
    DesembolsoSerializer, 
    DesembolsoWriteSerializer,
    CargoFijoSerializer, 
    GarantiaSerializer
)


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
