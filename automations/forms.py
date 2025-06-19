from django import forms
from .models import AutomatedProcess, ScheduledTask

class AutomatedProcessForm(forms.ModelForm):
    class Meta:
        model = AutomatedProcess
        fields = [
            'name',
            'description',
            'script_path',
            'virtual_env_path',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Proceso'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada del proceso'}),
            'script_path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/ruta/al/script.py'}),
            'virtual_env_path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/ruta/al/entorno_virtual (opcional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nombre del Proceso',
            'description': 'Descripción',
            'script_path': 'Ruta del Script Python',
            'virtual_env_path': 'Ruta del Entorno Virtual (Opcional)',
            'is_active': '¿Está activo?'
        }
        help_texts = {
            'script_path': 'La ruta absoluta al script de Python que se ejecutará.',
            'virtual_env_path': 'Si el script requiere un entorno virtual específico, indica la ruta a la carpeta raíz del venv.',
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


class ScheduledTaskForm(forms.ModelForm):
    class Meta:
        model = ScheduledTask
        fields = [
            'process', 
            'frecuencia', 
            'intervalo', 
            'hora_ejecucion', 
            'dia_semana', 
            'dia_mes', 
            'fecha_ejecucion_unica',
            'activo'
        ]
        widgets = {
            'hora_ejecucion': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha_ejecucion_unica': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'intervalo': forms.NumberInput(attrs={'placeholder': 'Ej. 15'}),
            'dia_mes': forms.NumberInput(attrs={'placeholder': 'Ej. 28', 'min': 1, 'max': 31}),
        }

    def __init__(self, *args, **kwargs):
        process_id = kwargs.pop('process_id', None)
        super().__init__(*args, **kwargs)

        # Siempre poblar el queryset con procesos activos y aplicar la clase CSS.
        self.fields['process'].queryset = AutomatedProcess.objects.filter(is_active=True).order_by('name')
        self.fields['process'].widget.attrs.update({'class': 'form-control'})

        if process_id:
            # Si venimos de la página de un proceso, lo pre-seleccionamos y deshabilitamos el campo.
            try:
                process = AutomatedProcess.objects.get(pk=process_id, is_active=True)
                self.fields['process'].initial = process
                self.fields['process'].disabled = True
            except AutomatedProcess.DoesNotExist:
                # Si el proceso no existe o está inactivo, mostramos el dropdown normal con un error.
                self.fields['process'].empty_label = "Proceso no válido o inactivo. Seleccione uno."
                self.fields['process'].disabled = False
        else:
            # Si es el formulario general, mostramos un placeholder.
            self.fields['process'].empty_label = "Seleccione un proceso para automatizar"

    def clean(self):
        cleaned_data = super().clean()
        frecuencia = cleaned_data.get('frecuencia')

        if frecuencia == 'MINUTOS' or frecuencia == 'HORAS':
            if not cleaned_data.get('intervalo'):
                self.add_error('intervalo', 'Este campo es requerido para la frecuencia seleccionada.')
        
        elif frecuencia == 'DIARIO':
            if not cleaned_data.get('hora_ejecucion'):
                self.add_error('hora_ejecucion', 'La hora de ejecución es requerida para la frecuencia diaria.')

        elif frecuencia == 'SEMANAL':
            if not cleaned_data.get('hora_ejecucion'):
                self.add_error('hora_ejecucion', 'La hora de ejecución es requerida.')
            if not cleaned_data.get('dia_semana'):
                self.add_error('dia_semana', 'El día de la semana es requerido.')

        elif frecuencia == 'MENSUAL':
            if not cleaned_data.get('hora_ejecucion'):
                self.add_error('hora_ejecucion', 'La hora de ejecución es requerida.')
            if not cleaned_data.get('dia_mes'):
                self.add_error('dia_mes', 'El día del mes es requerido.')

        elif frecuencia == 'UNA_VEZ':
            if not cleaned_data.get('fecha_ejecucion_unica'):
                self.add_error('fecha_ejecucion_unica', 'La fecha y hora son requeridas para una ejecución única.')

        return cleaned_data 