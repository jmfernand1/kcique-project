from django.shortcuts import render, redirect
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone
from .models import CasoDebito
from .forms import CSVUploadForm, CasoDebitoForm
import pandas as pd
import io # Para manejar el archivo en memoria
from django.contrib import messages # Para mostrar mensajes al usuario
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CasoDebitoSerializer
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
import csv
from datetime import datetime

# Reutilizaremos la lógica de carga del script, pero adaptada a una vista
# Idealmente, esta lógica podría estar en un archivo de 'servicios' o 'utils' de la app.

def procesar_y_cargar_csv(archivo_csv_subido, nombre_script='carga_web_adagio'):
    """
    Procesa un archivo CSV subido y carga los datos en el modelo CasoDebito.
    Retorna un resumen de la operación.
    """
    try:
        # Decodificar el archivo subido si es necesario, pandas puede manejar bytes directamente
        # Para archivos de texto, es mejor asegurarse de que esté en un formato que pandas pueda leer, como un StringIO
        try:
            archivo_csv_subido.seek(0)
            df = pd.read_csv(io.StringIO(archivo_csv_subido.read().decode('utf-8')))
        except UnicodeDecodeError:
            archivo_csv_subido.seek(0)
            df = pd.read_csv(io.StringIO(archivo_csv_subido.read().decode('latin-1')))
            
        # print(f"Columnas detectadas en el CSV: {df.columns.tolist()}") # Para depuración

    except Exception as e:
        return {"error": f"Error al leer el archivo CSV: {e}"}

    casos_creados = 0
    casos_actualizados = 0
    filas_con_error = 0
    errores_detalle = []

    required_columns = ['cod_caso_bizagi'] # Columnas mínimas esperadas
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return {"error": f"El archivo CSV no contiene las columnas requeridas: {', '.join(missing_cols)}"}

    for index, row in df.iterrows():
        try:
            cod_caso_bizagi = str(row['cod_caso_bizagi'])
            
            defaults = {
                'num_prestamo': str(row.get('num_prestamo', '')) or None,
                'docsoldv': str(row.get('docsoldv', '')) or None,
                'doctitulardv': str(row.get('doctitulardv', '')) or None,
                'tipo_de_cuenta': str(row.get('tipo_de_cuenta', '')) or None,
                'numcta_debito': str(row.get('numcta_debito', '')) or None,
                'secuencia_cta': str(row.get('secuencia_cta', '')) or None,
                'codigo_del_banco': str(row.get('codigo_del_banco', '')) or None,
                'codigo_ciudad': str(row.get('codigo_ciudad', '')) or None,
                'tipo_debito': str(row.get('tipo_debito', 'AL TITULAR')) or 'AL TITULAR',
                'autoriza': str(row.get('autoriza', '')) or None,
                'fecha_desembolso': str(row.get('fecha_desembolso', '')) or None,
                'estado': str(row.get('estado', 'PENDIENTE')) or 'PENDIENTE',
                'proceso_actualizador': nombre_script,
            }

            caso, creado = CasoDebito.objects.update_or_create(
                cod_caso_bizagi=cod_caso_bizagi,
                defaults=defaults
            )

            if creado:
                caso.proceso_creador = nombre_script
                caso.save()
                casos_creados += 1
            else:
                casos_actualizados += 1

        except KeyError as e:
            error_msg = f"Fila {index + 2}: Falta la columna {e}."
            errores_detalle.append(error_msg)
            filas_con_error +=1
        except Exception as e:
            error_msg = f"Fila {index + 2} (Caso {row.get('cod_caso_bizagi', 'N/A')}): {e}"
            errores_detalle.append(error_msg)
            filas_con_error +=1
    
    return {
        "creados": casos_creados,
        "actualizados": casos_actualizados,
        "errores": filas_con_error,
        "errores_detalle": errores_detalle
    }

def dashboard_adagio(request):
    # Estadísticas
    casos_pendientes = CasoDebito.objects.filter(estado='PENDIENTE').count()
    casos_grabado = CasoDebito.objects.filter(estado='GRABADO').count()
    casos_pendiente_bizagi = CasoDebito.objects.filter(estado='PENDIENTE BIZAGI').count()
    casos_finalizado = CasoDebito.objects.filter(estado='FINALIZADO').count()
    casos_con_error_db = CasoDebito.objects.filter(estado='CON ERROR').count()
    casos_validar_db = CasoDebito.objects.filter(estado='VALIDAR').count()
    total_casos = CasoDebito.objects.count()

    # Promedio de tiempo de ejecución para casos resueltos
    # Se calcula la diferencia entre fecha_fin_proceso y fecha_inicio_proceso
    casos_completados_con_tiempo = CasoDebito.objects.filter(
        estado='FINALIZADO',
        fecha_inicio_proceso__isnull=False,
        fecha_fin_proceso__isnull=False
    ).annotate(
        tiempo_ejecucion=ExpressionWrapper(F('fecha_fin_proceso') - F('fecha_inicio_proceso'), output_field=DurationField())
    )

    promedio_ejecucion_data = casos_completados_con_tiempo.aggregate(Avg('tiempo_ejecucion'))
    promedio_ejecucion = promedio_ejecucion_data['tiempo_ejecucion__avg']
    
    # Formulario de carga
    form = CSVUploadForm()

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # Validar tipo de archivo (opcional pero recomendado)
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Error: El archivo debe ser un CSV.')
            else:
                resultado_carga = procesar_y_cargar_csv(csv_file)
                if "error" in resultado_carga:
                    messages.error(request, resultado_carga["error"])
                else:
                    messages.success(request, f"Archivo CSV procesado. Creados: {resultado_carga['creados']}, Actualizados: {resultado_carga['actualizados']}, Errores: {resultado_carga['errores']}.")
                    if resultado_carga['errores_detalle']:
                        for err_detalle in resultado_carga['errores_detalle']:
                            messages.warning(request, err_detalle) # Muestra detalles de errores específicos
                return redirect('adagio:dashboard_adagio') # Redirige para evitar reenvío de formulario
        else:
            messages.error(request, "Error en el formulario de carga.")

    context = {
        'casos_pendientes': casos_pendientes,
        'casos_grabado': casos_grabado,
        'casos_pendiente_bizagi': casos_pendiente_bizagi,
        'casos_finalizado': casos_finalizado,
        'casos_con_error_db': casos_con_error_db,
        'casos_validar_db': casos_validar_db,
        'total_casos': total_casos,
        'promedio_ejecucion': promedio_ejecucion, # Puede ser None si no hay datos
        'form': form,
        'casos_recientes': CasoDebito.objects.all().order_by('-fecha_actualizacion')[:10] # Muestra los 10 más recientes
    }
    return render(request, 'adagio/dashboard.html', context)


class CasoDebitoListView(ListView):
    model = CasoDebito
    template_name = 'adagio/casopendiente_list.html'
    context_object_name = 'casos'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-fecha_creacion')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(cod_caso_bizagi__icontains=query) |
                Q(num_prestamo__icontains=query) |
                Q(docsoldv__icontains=query) |
                Q(autoriza__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CasoDebitoDetailView(DetailView):
    model = CasoDebito
    template_name = 'adagio/casopendiente_detail.html'
    context_object_name = 'caso'
    success_url = reverse_lazy('adagio:casopendiente_list')


class CasoDebitoCreateView(CreateView):
    model = CasoDebito
    form_class = CasoDebitoForm
    template_name = 'adagio/casopendiente_form.html'
    success_url = reverse_lazy('adagio:casopendiente_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nuevo Caso'
        return context


class CasoDebitoUpdateView(UpdateView):
    model = CasoDebito
    form_class = CasoDebitoForm
    template_name = 'adagio/casopendiente_form.html'
    success_url = reverse_lazy('adagio:casopendiente_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Caso'
        return context


class CasoDebitoDeleteView(DeleteView):
    model = CasoDebito
    template_name = 'adagio/casopendiente_confirm_delete.html'
    success_url = reverse_lazy('adagio:casopendiente_list')
    context_object_name = 'caso'


# API Views
class CasoDebitoViewSet(viewsets.ModelViewSet):
    """
    Endpoint de la API que permite ver o editar los casos de débito.
    """
    queryset = CasoDebito.objects.all().order_by('-fecha_creacion')
    serializer_class = CasoDebitoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado', 'cod_caso_bizagi', 'num_prestamo']


# Vistas de descarga CSV
def generar_csv_response(queryset, filename_prefix):
    """
    Función auxiliar para generar respuesta CSV desde un queryset de CasoDebito
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{timestamp}.csv"'
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    writer.writerow([
        'ID', 'Código Caso Bizagi', 'Número Préstamo', 'Documentos Solicitados', 
        'Documento Titular', 'Tipo de Cuenta', 'Número Cuenta Débito', 
        'Secuencia Cuenta', 'Código del Banco', 'Código Ciudad', 'Tipo Débito',
        'Autoriza', 'Fecha Desembolso', 'Estado', 'Fecha Creación', 
        'Fecha Actualización', 'Fecha Inicio Proceso', 'Fecha Fin Proceso',
        'Proceso Creador', 'Proceso Actualizador', 'Intentos Procesamiento',
        'Último Error'
    ])
    
    # Escribir datos
    for caso in queryset:
        writer.writerow([
            caso.id,
            caso.cod_caso_bizagi,
            caso.num_prestamo or '',
            caso.docsoldv or '',
            caso.doctitulardv or '',
            caso.tipo_de_cuenta or '',
            caso.numcta_debito or '',
            caso.secuencia_cta or '',
            caso.codigo_del_banco or '',
            caso.codigo_ciudad or '',
            caso.tipo_debito,
            caso.autoriza or '',
            caso.fecha_desembolso or '',
            caso.estado,
            caso.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if caso.fecha_creacion else '',
            caso.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S') if caso.fecha_actualizacion else '',
            caso.fecha_inicio_proceso.strftime('%Y-%m-%d %H:%M:%S') if caso.fecha_inicio_proceso else '',
            caso.fecha_fin_proceso.strftime('%Y-%m-%d %H:%M:%S') if caso.fecha_fin_proceso else '',
            caso.proceso_creador or '',
            caso.proceso_actualizador or '',
            caso.intentos_procesamiento,
            caso.ultimo_error or ''
        ])
    
    return response


def descargar_todos_casos(request):
    """Vista para descargar todos los casos"""
    queryset = CasoDebito.objects.all().order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'todos_los_casos')


def descargar_casos_pendientes(request):
    """Vista para descargar casos pendientes"""
    queryset = CasoDebito.objects.filter(estado='PENDIENTE').order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'casos_pendientes')


def descargar_casos_pendiente_bizagi(request):
    """Vista para descargar casos pendiente bizagi"""
    queryset = CasoDebito.objects.filter(estado='PENDIENTE BIZAGI').order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'casos_pendiente_bizagi')


def descargar_casos_grabado(request):
    """Vista para descargar casos grabados"""
    queryset = CasoDebito.objects.filter(estado='GRABADO').order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'casos_grabado')


def descargar_casos_finalizado(request):
    """Vista para descargar casos finalizados"""
    queryset = CasoDebito.objects.filter(estado='FINALIZADO').order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'casos_finalizado')


def descargar_casos_con_error(request):
    """Vista para descargar casos con error"""
    queryset = CasoDebito.objects.filter(estado='CON ERROR').order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'casos_con_error')


def descargar_casos_validar(request):
    """Vista para descargar casos a validar"""
    queryset = CasoDebito.objects.filter(estado='VALIDAR').order_by('-fecha_creacion')
    return generar_csv_response(queryset, 'casos_validar')
