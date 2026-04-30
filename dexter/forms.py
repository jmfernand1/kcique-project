from django import forms
from django.forms import inlineformset_factory
from .models import Desembolso, CargoFijo, Garantia, TipoDesembolso


class DesembolsoForm(forms.ModelForm):
    """Formulario para crear/editar Desembolsos"""
    
    class Meta:
        model = Desembolso
        fields = [
            'referencia', 'obligacion', 'id_cliente', 'nit_beneficiario',
            'aliado', 'tipo_cta_destino', 'cod_tipo_cuenta_destino',
            'num_cta_destino', 'banco_destino', 'cod_banco_destino',
            'valor_desembolso', 'numero_tramos', 'plazo_tramo_1',
            'tipo_tasa_tramo_1', 'tasa_tramo_1', 'amortizacion_tramo_1',
            'plazo_tramo_2', 'tipo_tasa_tramo_2', 'tasa_tramo_2',
            'amortizacion_tramo_2', 'dia_pago_cuota', 'estado', 'tipo_desembolso'
        ]
        widgets = {
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'REF-001'}),
            'obligacion': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_cliente': forms.NumberInput(attrs={'class': 'form-control'}),
            'nit_beneficiario': forms.NumberInput(attrs={'class': 'form-control'}),
            'aliado': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_cta_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_tipo_cuenta_destino': forms.NumberInput(attrs={'class': 'form-control'}),
            'num_cta_destino': forms.NumberInput(attrs={'class': 'form-control'}),
            'banco_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_banco_destino': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_desembolso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'numero_tramos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '2'}),
            'plazo_tramo_1': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_tasa_tramo_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FIJA/VARIABLE'}),
            'tasa_tramo_1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amortizacion_tramo_1': forms.TextInput(attrs={'class': 'form-control'}),
            'plazo_tramo_2': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_tasa_tramo_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FIJA/VARIABLE'}),
            'tasa_tramo_2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amortizacion_tramo_2': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_pago_cuota': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_desembolso': forms.Select(attrs={'class': 'form-control'}),
        }


class CargoFijoForm(forms.ModelForm):
    """Formulario para crear/editar Cargos Fijos"""
    
    class Meta:
        model = CargoFijo
        fields = ['codigo', 'nombre_cargo_fijo', 'fecha_efectiva', 'fecha_revision', 'periodicidad', 'valor']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CF001'}),
            'nombre_cargo_fijo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_efectiva': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_revision': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'periodicidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MENSUAL/ANUAL'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


# Formset para manejar múltiples CargoFijo en el formulario de Desembolso
CargoFijoFormSet = inlineformset_factory(
    Desembolso, 
    CargoFijo,
    form=CargoFijoForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class GarantiaForm(forms.ModelForm):
    """Formulario para crear/editar Garantías"""
    
    class Meta:
        model = Garantia
        fields = [
            'referencia', 'obligacion', 'id_cliente', 'id_garante',
            'cod_fasecolda', 'codigo_fasecolda', 'color', 'placa',
            'poliza_vehiculo', 'cod_aseguradora', 'nro_poliza',
            'valor_asegurado', 'fecha_vencimiento_seguro', 'tipo_prima',
            'valor_prima', 'folio_electronico', 'valor_vehiculo',
            'modelo', 'fecha_prenda', 'chasis', 'motor', 'serie',
            'servicio', 'fecha_desembolso', 'estado'
        ]
        widgets = {
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'obligacion': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_cliente': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_garante': forms.NumberInput(attrs={'class': 'form-control'}),
            'cod_fasecolda': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_fasecolda': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC123'}),
            'poliza_vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_aseguradora': forms.TextInput(attrs={'class': 'form-control'}),
            'nro_poliza': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_asegurado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_vencimiento_seguro': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_prima': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_prima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'folio_electronico': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_vehiculo': forms.NumberInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2024'}),
            'fecha_prenda': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'chasis': forms.TextInput(attrs={'class': 'form-control'}),
            'motor': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_desembolso': forms.DateInput(format='%Y-%m-%d',attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }

