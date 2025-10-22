# En tu ETL externo (sin Django)
from etl_tracking_client import ETLTrackingClient

# 1. Conectar a la API
client = ETLTrackingClient("http://localhost:8000/dexter/api")

# 2. Iniciar ejecución
ejecucion_id = client.iniciar_ejecucion_desembolso(total_registros=100)
mis_desembolsos = 

# 3. Procesar cada desembolso
for desembolso_id in mis_desembolsos:
    proceso_id = client.crear_proceso_desembolso(ejecucion_id, desembolso_id)
    
    try:
        # Tu lógica de etapa 1
        try:
            grabar_cargos_fijos(desembolso_id)
            client.avanzar_etapa_desembolso(proceso_id, 'GRABAR_CARGOS_FIJOS')
        except Exception as e:
            client.marcar_error_desembolso(proceso_id, str(e))
        
        # Tu lógica de etapa 2
        ejecutar_desembolso(desembolso_id)
        client.avanzar_etapa_desembolso(proceso_id, 'DESEMBOLSO')
        
        # ... resto de etapas
        
        client.completar_proceso_desembolso(proceso_id)
    except Exception as e:
        client.marcar_error_desembolso(proceso_id, str(e))

# 4. Finalizar
client.completar_ejecucion(ejecucion_id)