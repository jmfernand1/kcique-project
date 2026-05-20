from rest_framework import serializers
from .models import (
    Desembolso, 
    CargoFijo, 
    Garantia, 
    EjecucionETL, 
    ProcesoDesembolso, 
    ProcesoGarantia, 
    EtapaProcesoDesembolso,
    EtapaProcesoGarantia,
    TipoDesembolso, 
    TipoGarantia, 
    EtapaTipoDesembolso, 
    EtapaTipoGarantia
    )

import datetime
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

# ============================================================================
# SERIALIZERS DE DATOS PRINCIPALES
# ============================================================================

@extend_schema_field(OpenApiTypes.INT)
class YyyyMmDdDateField(serializers.Field):
    """
    API <-> Modelo:
    - to_internal_value: convierte 20260131 / "20260131" / "2026-01-31" a date
    - to_representation: convierte date -> 20260131 (int)
    """
    def to_internal_value(self, data):
        if data in (None, "", 0):
            return None

        # Normalizamos a string para parseo
        if isinstance(data, int):
            s = str(data)
        elif isinstance(data, str):
            s = data.strip()
            # Soportar "YYYY-MM-DD"
            if "-" in s:
                try:
                    return datetime.datetime.strptime(s, "%Y-%m-%d").date()
                except ValueError:
                    raise serializers.ValidationError("Fecha inválida. Use YYYYMMDD o YYYY-MM-DD.")
        else:
            raise serializers.ValidationError("Tipo inválido. Use entero YYYYMMDD o string.")

        # Validar "YYYYMMDD"
        if len(s) != 8 or not s.isdigit():
            raise serializers.ValidationError("Formato inválido. Use YYYYMMDD (8 dígitos).")

        try:
            return datetime.datetime.strptime(s, "%Y%m%d").date()
        except ValueError:
            raise serializers.ValidationError("Fecha inexistente (revise día/mes).")

    def to_representation(self, value):
        if value in (None, ""):
            return None
        if isinstance(value, datetime.datetime):
            value = value.date()
        return int(value.strftime("%Y%m%d"))


class CargoFijoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo CargoFijo"""
    
    fecha_efectiva = YyyyMmDdDateField(required=False, allow_null=True)
    fecha_revision = YyyyMmDdDateField(required=False, allow_null=True)

    class Meta:
        model = CargoFijo
        fields = '__all__'


class DesembolsoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Desembolso con cargos fijos incluidos"""
    cargos_fijos = CargoFijoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Desembolso
        fields = '__all__'


class DesembolsoWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar Desembolso sin cargos fijos anidados"""
    class Meta:
        model = Desembolso
        fields = '__all__'


class GarantiaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Garantia"""
    fecha_desembolso = YyyyMmDdDateField(required=False, allow_null=True)
    fecha_prenda = YyyyMmDdDateField(required=False, allow_null=True)   
    fecha_vencimiento_seguro = YyyyMmDdDateField(required=False, allow_null=True)
    
    class Meta:
        model = Garantia
        fields = '__all__'


# ============================================================================
# SERIALIZERS DE TRACKING ETL
# ============================================================================

class EjecucionETLSerializer(serializers.ModelSerializer):
    """Serializer para EjecucionETL"""
    progreso = serializers.SerializerMethodField()
    
    class Meta:
        model = EjecucionETL
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_fin']
    
    def get_progreso(self, obj):
        """Calcula el porcentaje de progreso"""
        if obj.total_registros == 0:
            return 0
        return round((obj.registros_procesados / obj.total_registros) * 100, 2)


class EtapaProcesoDesembolsoSerializer(serializers.ModelSerializer):
    """Serializer para EtapaProcesoDesembolso"""
    etapa_nombre = serializers.CharField(source='etapa.nombre', read_only=True)
    etapa_descripcion = serializers.CharField(source='etapa.descripcion', read_only=True)
    
    class Meta:
        model = EtapaProcesoDesembolso
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_inicio', 'fecha_completado']


class ProcesoDesembolsoSerializer(serializers.ModelSerializer):
    """Serializer para ProcesoDesembolso"""
    desembolso_referencia = serializers.CharField(source='desembolso.referencia', read_only=True)
    etapas = EtapaProcesoDesembolsoSerializer(many=True, read_only=True)
    etapa_actual_info = serializers.SerializerMethodField()
    siguiente_etapa_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcesoDesembolso
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_completado']
    
    def get_etapa_actual_info(self, obj):
        """Retorna información de la etapa actual"""
        etapa = obj.etapa_actual
        if etapa:
            return {
                'id': etapa.id,
                'nombre': etapa.etapa.nombre,
                'estado': etapa.estado,
                'orden': etapa.orden
            }
        return None
    
    def get_siguiente_etapa_info(self, obj):
        """Retorna información de la siguiente etapa"""
        etapa = obj.siguiente_etapa
        if etapa:
            return {
                'id': etapa.id,
                'nombre': etapa.etapa.nombre,
                'estado': etapa.estado,
                'orden': etapa.orden
            }
        return None


class EtapaProcesoGarantiaSerializer(serializers.ModelSerializer):
    """Serializer para EtapaProcesoGarantia"""
    etapa_nombre = serializers.CharField(source='etapa.nombre', read_only=True)
    etapa_descripcion = serializers.CharField(source='etapa.descripcion', read_only=True)
    
    class Meta:
        model = EtapaProcesoGarantia
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_inicio', 'fecha_completado']


class ProcesoGarantiaSerializer(serializers.ModelSerializer):
    """Serializer para ProcesoGarantia"""
    garantia_placa = serializers.CharField(source='garantia.placa', read_only=True)
    etapas = EtapaProcesoGarantiaSerializer(many=True, read_only=True)
    etapa_actual_info = serializers.SerializerMethodField()
    siguiente_etapa_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcesoGarantia
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_completado']
    
    def get_etapa_actual_info(self, obj):
        """Retorna información de la etapa actual"""
        etapa = obj.etapa_actual
        if etapa:
            return {
                'id': etapa.id,
                'nombre': etapa.etapa.nombre,
                'estado': etapa.estado,
                'orden': etapa.orden
            }
        return None
    
    def get_siguiente_etapa_info(self, obj):
        """Retorna información de la siguiente etapa"""
        etapa = obj.siguiente_etapa
        if etapa:
            return {
                'id': etapa.id,
                'nombre': etapa.etapa.nombre,
                'estado': etapa.estado,
                'orden': etapa.orden
            }
        return None


class EtapaTipoDesembolsoSerializer(serializers.ModelSerializer):
    """Serializer para EtapaTipoDesembolso"""
    class Meta:
        model = EtapaTipoDesembolso
        fields = '__all__'

class TipoDesembolsoSerializer(serializers.ModelSerializer):
    """Serializer para TipoDesembolso"""

    etapas = EtapaTipoDesembolsoSerializer(many=True, read_only=True)
    class Meta:
        model = TipoDesembolso
        fields = '__all__'

class TipoGarantiaSerializer(serializers.ModelSerializer):
    """Serializer para TipoGarantia"""
    class Meta:
        model = TipoGarantia
        fields = '__all__'



class EtapaTipoGarantiaSerializer(serializers.ModelSerializer):
    """Serializer para EtapaTipoGarantia"""
    class Meta:
        model = EtapaTipoGarantia
        fields = '__all__'