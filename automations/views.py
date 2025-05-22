from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from .models import AutomatedProcess, ProcessLog
from .forms import AutomatedProcessForm
from .process_executor import run_process_threaded # Importamos la función

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
