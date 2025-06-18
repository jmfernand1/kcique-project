from rest_framework import serializers
from .models import CasoDebito

class CasoDebitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasoDebito
        fields = '__all__' 