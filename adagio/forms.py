from django import forms
from .models import CasoDebito

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Selecciona un archivo CSV')

class CasoDebitoForm(forms.ModelForm):
    class Meta:
        model = CasoDebito
        fields = '__all__'
        widgets = {
            'fecha_inicio_proceso': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin_proceso': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'datos_adicionales': forms.Textarea(attrs={'rows': 3}),
            'ultimo_error': forms.Textarea(attrs={'rows': 3}),
        } 