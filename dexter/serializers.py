from rest_framework import serializers
from .models import Desembolso, CargoFijo, Garantia, EjecucionETL, ProcesoDesembolso, ProcesoGarantia


# ============================================================================
# SERIALIZERS DE DATOS PRINCIPALES
# ============================================================================

class CargoFijoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo CargoFijo"""
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


class ProcesoDesembolsoSerializer(serializers.ModelSerializer):
    """Serializer para ProcesoDesembolso"""
    desembolso_referencia = serializers.CharField(source='desembolso.referencia', read_only=True)
    
    class Meta:
        model = ProcesoDesembolso
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_ultima_actualizacion', 'fecha_completado']


class ProcesoGarantiaSerializer(serializers.ModelSerializer):
    """Serializer para ProcesoGarantia"""
    garantia_placa = serializers.CharField(source='garantia.placa', read_only=True)
    
    class Meta:
        model = ProcesoGarantia
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_ultima_actualizacion', 'fecha_completado']
