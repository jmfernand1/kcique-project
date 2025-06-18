from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from .models import AutomatedProcess, ProcessLog, ScheduledTask
from .forms import AutomatedProcessForm, ScheduledTaskForm
from .process_executor import run_process_threaded # Importamos la función
from django_q.tasks import schedule
from django_q.models import Schedule
from django.utils import timezone

# Vista para la página de inicio
def home_view(request):
    return render(request, 'home.html')

class ProcessListView(ListView):
    model = AutomatedProcess
    template_name = 'automations/process_list.html'
    context_object_name = 'processes'
    paginate_by = 10

    def get_queryset(self):
        return AutomatedProcess.objects.all().order_by('-created_at')

# Vista basada en función para la lista (alternativa si se necesita más personalización)
# def process_list(request):
#     processes = AutomatedProcess.objects.all().order_by('-created_at')
#     return render(request, 'automations/process_list.html', {'processes': processes})

process_list = ProcessListView.as_view() # Usaremos la vista basada en clase por ahora

class ProcessDetailView(DetailView):
    model = AutomatedProcess
    template_name = 'automations/process_detail.html'
    context_object_name = 'process'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logs'] = ProcessLog.objects.filter(process=self.object).order_by('-start_time')[:20] # Últimos 20 logs
        return context

process_detail = ProcessDetailView.as_view()

class ProcessCreateView(CreateView):
    model = AutomatedProcess
    form_class = AutomatedProcessForm
    template_name = 'automations/process_form.html'
    success_url = reverse_lazy('automations:process_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Proceso Automatizado'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Proceso creado exitosamente.")
        return super().form_valid(form)

process_create = ProcessCreateView.as_view()

class ProcessUpdateView(UpdateView):
    model = AutomatedProcess
    form_class = AutomatedProcessForm
    template_name = 'automations/process_form.html'
    success_url = reverse_lazy('automations:process_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Actualizar Proceso: {self.object.name}'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Proceso actualizado exitosamente.")
        return super().form_valid(form)

process_update = ProcessUpdateView.as_view()

class ProcessDeleteView(DeleteView):
    model = AutomatedProcess
    template_name = 'automations/process_confirm_delete.html'
    success_url = reverse_lazy('automations:process_list')

    def post(self, request, *args, **kwargs):
        messages.success(self.request, f"Proceso '{self.get_object().name}' eliminado exitosamente.")
        return super().post(request, *args, **kwargs)

process_delete = ProcessDeleteView.as_view()

def run_process_view(request, process_id):
    process = get_object_or_404(AutomatedProcess, pk=process_id)
    if not process.is_active:
        messages.error(request, f"El proceso '{process.name}' no está activo y no puede ser ejecutado.")
        return redirect('automations:process_detail', pk=process_id)
    
    run_process_threaded(process_id) # Llamamos a la función del executor
    messages.info(request, f"Ejecución del proceso '{process.name}' iniciada en segundo plano.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('automations:process_detail', kwargs={'pk': process_id})))

def get_log_output(request, log_id):
    log = get_object_or_404(ProcessLog, pk=log_id)
    return JsonResponse({
        'output_log': log.output_log,
        'status': log.status,
        'end_time': log.end_time.strftime('%Y-%m-%d %H:%M:%S') if log.end_time else None
    })

# --- Vistas para Tareas Programadas (ScheduledTask) ---

def _programar_en_django_q(tarea: ScheduledTask):
    """Crea o actualiza una tarea en Django Q para un Proceso Automatizado."""
    
    # Nombre único para la tarea en Django Q
    nombre_tarea_q = f"scheduled-process-{tarea.pk}"

    # Si la tarea ya tiene un ID en Q, la borramos para evitar duplicados.
    if tarea.id_tarea_django_q:
        try:
            Schedule.objects.filter(name=tarea.id_tarea_django_q).delete()
        except Schedule.DoesNotExist:
            pass # No pasa nada si no existía

    # Si la tarea no está activa, no la programamos.
    if not tarea.activo:
        tarea.id_tarea_django_q = ''
        tarea.save(update_fields=['id_tarea_django_q'])
        return

    opciones = {
        'func': 'automations.tasks.execute_automated_process',
        'args': f'{tarea.process.id}', # Pasamos el ID del proceso a ejecutar
        'name': nombre_tarea_q,
        'repeats': -1, # Repetir indefinidamente por defecto
        'cluster': 'default'
    }

    if tarea.frecuencia == 'UNA_VEZ':
        opciones['schedule_type'] = Schedule.ONCE
        opciones['next_run'] = tarea.fecha_ejecucion_unica
        opciones['repeats'] = 0
    elif tarea.frecuencia == 'MINUTOS':
        opciones['schedule_type'] = Schedule.MINUTES
        opciones['minutes'] = tarea.intervalo
    elif tarea.frecuencia == 'HORAS':
        opciones['schedule_type'] = Schedule.HOURLY
        opciones['hours'] = tarea.intervalo
    elif tarea.frecuencia == 'DIARIO':
        opciones['schedule_type'] = Schedule.DAILY
        opciones['next_run'] = timezone.now().replace(hour=tarea.hora_ejecucion.hour, minute=tarea.hora_ejecucion.minute)
    elif tarea.frecuencia == 'SEMANAL':
        opciones['schedule_type'] = Schedule.WEEKLY
        # Nota: django-q usa el día de la semana de next_run. Podríamos calcularlo
        # exactamente, pero por simplicidad lo dejamos que se ajuste solo.
        opciones['next_run'] = timezone.now().replace(hour=tarea.hora_ejecucion.hour, minute=tarea.hora_ejecucion.minute)
    elif tarea.frecuencia == 'MENSUAL':
        opciones['schedule_type'] = Schedule.MONTHLY
        opciones['day_of_month'] = str(tarea.dia_mes)
        opciones['next_run'] = timezone.now().replace(hour=tarea.hora_ejecucion.hour, minute=tarea.hora_ejecucion.minute)
    
    # Crear la nueva tarea programada
    s = schedule(**opciones)
    
    # Guardar el nombre único de la tarea de Django Q para futuras referencias
    tarea.id_tarea_django_q = nombre_tarea_q
    tarea.save(update_fields=['id_tarea_django_q'])

class ScheduledTaskListView(ListView):
    model = ScheduledTask
    template_name = 'automations/scheduledtask_list.html'
    context_object_name = 'tareas'

class ScheduledTaskCreateView(CreateView):
    model = ScheduledTask
    form_class = ScheduledTaskForm
    template_name = 'automations/scheduledtask_form.html'
    success_url = reverse_lazy('automations:scheduledtask_list')

    def get_form_kwargs(self):
        """Pasa el process_id de la URL al formulario si está presente."""
        kwargs = super().get_form_kwargs()
        if 'process_pk' in self.kwargs:
            kwargs['process_id'] = self.kwargs['process_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'process_pk' in self.kwargs:
            process = get_object_or_404(AutomatedProcess, pk=self.kwargs['process_pk'])
            context['titulo'] = f'Programar Tarea para: {process.name}'
        else:
            context['titulo'] = 'Programar Nueva Tarea'
        return context

    def form_valid(self, form):
        self.object = form.save()
        _programar_en_django_q(self.object)
        if self.object.activo:
            messages.success(self.request, f"La tarea para '{self.object.process.name}' ha sido programada.")
        else:
            messages.info(self.request, f"La tarea ha sido guardada como inactiva.")
        return HttpResponseRedirect(self.get_success_url())

class ScheduledTaskUpdateView(UpdateView):
    model = ScheduledTask
    form_class = ScheduledTaskForm
    template_name = 'automations/scheduledtask_form.html'
    success_url = reverse_lazy('automations:scheduledtask_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editando Programación para: {self.object.process.name}'
        return context

    def form_valid(self, form):
        self.object = form.save()
        _programar_en_django_q(self.object)
        if self.object.activo:
            messages.success(self.request, f"La programación para '{self.object.process.name}' ha sido actualizada.")
        else:
            messages.success(self.request, f"La programación para '{self.object.process.name}' ha sido desactivada.")
        return HttpResponseRedirect(self.get_success_url())

class ScheduledTaskDeleteView(DeleteView):
    model = ScheduledTask
    template_name = 'automations/scheduledtask_confirm_delete.html'
    success_url = reverse_lazy('automations:scheduledtask_list')

    def form_valid(self, form):
        # La vista DeleteView se encarga de llamar a self.object.delete()
        # que es lo que queremos. Solo necesitamos asegurarnos de que la tarea
        # correspondiente en django-q también se elimine.
        self.object = self.get_object()
        
        # Eliminar la tarea de django-q usando su modelo
        if self.object.id_tarea_django_q:
            Schedule.objects.filter(name=self.object.id_tarea_django_q).delete()
        
        nombre_proceso = self.object.process.name
        messages.success(self.request, f"La programación para el proceso '{nombre_proceso}' ha sido eliminada.")
        
        # Dejamos que la clase base complete la eliminación del objeto ScheduledTask
        return super().form_valid(form)
