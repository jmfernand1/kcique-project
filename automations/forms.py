from django import forms
from .models import AutomatedProcess

class AutomatedProcessForm(forms.ModelForm):
    class Meta:
        model = AutomatedProcess
        fields = [
            'name',
            'description',
            'script_path',
            'virtual_env_path',
            'cron_schedule',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Proceso'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada del proceso'}),
            'script_path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/ruta/al/script.py'}),
            'virtual_env_path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/ruta/al/entorno_virtual (opcional)'}),
            'cron_schedule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0 5 * * * (opcional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nombre del Proceso',
            'description': 'Descripción',
            'script_path': 'Ruta del Script Python',
            'virtual_env_path': 'Ruta del Entorno Virtual (Opcional)',
            'cron_schedule': 'Programación Cron (Opcional)',
            'is_active': '¿Está activo?'
        }
        help_texts = {
            'script_path': 'La ruta absoluta al script de Python que se ejecutará.',
            'virtual_env_path': 'Si el script requiere un entorno virtual específico, indica la ruta a la carpeta raíz del venv.',
            'cron_schedule': 'Formato Cron para la programación. Ej: "0 0 * * *" para ejecutar todos los días a medianoche.',
        }

    def clean_script_path(self):
        script_path = self.cleaned_data.get('script_path')
        # Podríamos añadir validación para verificar si el archivo existe, pero
        # esto podría ser problemático si el servidor Django no tiene acceso directo
        # a todos los paths de los scripts en el momento de la creación/edición.
        # Por ahora, solo nos aseguramos de que no esté vacío.
        if not script_path:
            raise forms.ValidationError("La ruta del script no puede estar vacía.")
        return script_path 