import pandas as pd
import os
import django
import sys
from datetime import datetime

# Configura el entorno de Django
# Ajusta la ruta a tu proyecto Django según sea necesario
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kcique_project.settings') # Reemplaza 'kcique_project' con el nombre de tu proyecto Django
django.setup()

from adagio.models import CasoDebito # Asegúrate que 'adagio' es el nombre de tu app

def cargar_casos_desde_csv(ruta_csv, nombre_script='cargar_casos.py'):
    """
    Lee un archivo CSV con casos pendientes y los carga en el modelo CasoDebito.

    Args:
        ruta_csv (str): Ruta al archivo CSV.
        nombre_script (str): Nombre del script que realiza la carga (para trazabilidad).
    """
    try:
        df = pd.read_csv(ruta_csv)
        print(f"Se leyeron {len(df)} filas del archivo CSV: {ruta_csv}")
    except FileNotFoundError:
        print(f"Error: El archivo CSV no se encontró en la ruta: {ruta_csv}")
        return
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    casos_creados = 0
    casos_actualizados = 0
    casos_con_error = 0

    for index, row in df.iterrows():
        try:
            # Asume que los nombres de las columnas en el CSV coinciden con los esperados.
            # Realiza el mapeo explícito para mayor claridad y manejo de posibles diferencias.
            cod_caso_bizagi = str(row['cod_caso_bizagi']) # Campo obligatorio y único
            
            # Busca si el caso ya existe
            caso, creado = CasoDebito.objects.update_or_create(
                cod_caso_bizagi=cod_caso_bizagi,
                defaults={
                    'num_prestamo': str(row.get('num_prestamo', '')) or None,
                    'docsoldv': str(row.get('docsoldv', '')) or None,
                    'tipo_de_cuenta': str(row.get('tipo_de_cuenta', '')) or None,
                    'numcta_debito': str(row.get('numcta_debito', '')) or None,
                    'secuencia_cta': str(row.get('secuencia_cta', '')) or None,
                    'codigo_del_banco': str(row.get('codigo_del_banco', '')) or None,
                    'codigo_ciudad': str(row.get('codigo_ciudad', '')) or None,
                    'estado': str(row.get('estado', 'PENDIENTE')) or 'PENDIENTE', # Asigna PENDIENTE por defecto si no viene
                    'proceso_creador': nombre_script if creado else F('proceso_creador'), # No sobrescribir si ya existe
                    'proceso_actualizador': nombre_script,
                    # 'fecha_inicio_proceso': None, # Podrías establecerlo si el CSV lo indica
                    # 'fecha_fin_proceso': None,   # Podrías establecerlo si el CSV lo indica
                }
            )

            if creado:
                casos_creados += 1
                print(f"Caso creado: {cod_caso_bizagi}")
            else:
                casos_actualizados += 1
                print(f"Caso actualizado: {cod_caso_bizagi}")

        except KeyError as e:
            print(f"Error de mapeo en la fila {index + 2}: Falta la columna {e} en el CSV. Caso omitido: {row.get('cod_caso_bizagi', 'N/A')}")
            casos_con_error +=1
        except Exception as e:
            print(f"Error al procesar la fila {index + 2} para el caso {row.get('cod_caso_bizagi', 'N/A')}: {e}")
            casos_con_error +=1
            # Opcional: registrar el error en el campo ultimo_error del modelo si se puede identificar el caso
            # if 'cod_caso_bizagi' in row:
            #     CasoDebito.objects.filter(cod_caso_bizagi=row['cod_caso_bizagi']).update(
            #         ultimo_error=str(e), 
            #         proceso_actualizador=nombre_script,
            #         estado='ERROR' # Podrías marcarlo como error
            #     )


    print(f"\nResumen de la carga:")
    print(f"Casos creados: {casos_creados}")
    print(f"Casos actualizados: {casos_actualizados}")
    print(f"Casos con error: {casos_con_error}")

if __name__ == '__main__':
    # Reemplaza 'casos_pendientes.csv' con el nombre de tu archivo CSV si es diferente.
    # El script espera que el CSV esté en la raíz de tu proyecto Django.
    ruta_del_csv = os.path.join(project_path, 'casos_pendientes.csv') 
    
    print(f"Iniciando la carga de casos desde: {ruta_del_csv}")
    cargar_casos_desde_csv(ruta_del_csv)
    print("Proceso de carga finalizado.")

# Para ejecutar este script:
# 1. Asegúrate de tener pandas instalado: pip install pandas
# 2. Coloca tu archivo CSV (ej. casos_pendientes.csv) en la raíz de tu proyecto Django.
# 3. Ejecuta el script desde la raíz de tu proyecto Django: python scripts/cargar_casos.py 