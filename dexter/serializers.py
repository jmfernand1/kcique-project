from rest_framework import serializers
from .models import Desembolso, CargoFijo, Garantia


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

