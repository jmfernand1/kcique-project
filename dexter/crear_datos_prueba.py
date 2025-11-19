"""
Script para crear datos de prueba para el frontend de Dexter

Uso:
    python manage.py shell < dexter/crear_datos_prueba.py
    
O directamente en el shell de Django:
    from dexter.crear_datos_prueba import crear_datos_prueba
    crear_datos_prueba()
"""

from django.utils import timezone
from datetime import timedelta
import random
from dexter.models import (
    EjecucionETL, 
    ProcesoDesembolso, 
    ProcesoGarantia,
    Desembolso,
    Garantia,
    CargoFijo
)


def crear_datos_prueba():
    """
    Crea datos de prueba para visualizar el frontend de Dexter
    """
    print("🚀 Iniciando creación de datos de prueba para Dexter...\n")
    
    # Limpiar datos anteriores (opcional - comentar si no se desea)
    # EjecucionETL.objects.all().delete()
    # print("✅ Datos anteriores limpiados\n")
    
    # ========================================================================
    # CREAR DESEMBOLSOS DE PRUEBA
    # ========================================================================
    print("📋 Creando desembolsos de prueba...")
    desembolsos = []
    for i in range(15):
        desembolso = Desembolso.objects.create(
            referencia=f"DES-2024-{1000 + i}",
            obligacion=2000000000 + i,
            id_cliente=1000000 + i,
            nit_beneficiario=900000000 + i,
            aliado=random.choice(["Aliado A", "Aliado B", "Aliado C"]),
            tipo_cta_destino="Ahorros",
            cod_tipo_cuenta_destino=1,
            num_cta_destino=1234567890 + i,
            banco_destino=random.choice(["Bancolombia", "Davivienda", "BBVA"]),
            cod_banco_destino=random.choice([1, 2, 3]),
            valor_desembolso=random.uniform(10000000, 50000000),
            numero_tramos=2,
            plazo_tramo_1=36,
            tipo_tasa_tramo_1="EA",
            tasa_tramo_1=random.uniform(15.0, 25.0),
            amortizacion_tramo_1="FRANCES",
            plazo_tramo_2=12,
            tipo_tasa_tramo_2="EA",
            tasa_tramo_2=random.uniform(15.0, 25.0),
            amortizacion_tramo_2="FRANCES",
            dia_pago_cuota=15,
            estado="ACTIVO"
        )
        desembolsos.append(desembolso)
        
        # Crear cargos fijos para algunos desembolsos
        if i % 3 == 0:
            CargoFijo.objects.create(
                desembolso=desembolso,
                codigo="SEG001",
                nombre_cargo_fijo="Seguro de Vida",
                fecha_efectiva=timezone.now().date(),
                periodicidad="MENSUAL",
                valor=random.uniform(50000, 100000)
            )
    
    print(f"✅ Creados {len(desembolsos)} desembolsos\n")
    
    # ========================================================================
    # CREAR GARANTÍAS DE PRUEBA
    # ========================================================================
    print("🚗 Creando garantías de prueba...")
    garantias = []
    placas = ["ABC123", "XYZ789", "DEF456", "GHI012", "JKL345", 
              "MNO678", "PQR901", "STU234", "VWX567", "YZA890"]
    
    for i, placa in enumerate(placas):
        garantia = Garantia.objects.create(
            referencia=f"GAR-2024-{2000 + i}",
            obligacion=3000000000 + i,
            id_cliente=2000000 + i,
            id_garante=3000000 + i,
            cod_fasecolda=f"8{random.randint(10000, 99999)}",
            codigo_fasecolda=f"FAC{random.randint(100, 999)}",
            color=random.choice(["BLANCO", "NEGRO", "GRIS", "ROJO", "AZUL"]),
            placa=placa,
            poliza_vehiculo=f"POL{random.randint(100000, 999999)}",
            cod_aseguradora=str(random.randint(1, 10)),
            nro_poliza=f"NRO{random.randint(100000, 999999)}",
            valor_asegurado=random.uniform(20000000, 80000000),
            tipo_prima="ANUAL",
            valor_prima=random.uniform(1000000, 5000000),
            valor_vehiculo=random.randint(20000000, 80000000),
            modelo=str(random.randint(2018, 2024)),
            chasis=f"CHA{random.randint(100000, 999999)}",
            motor=f"MOT{random.randint(100000, 999999)}",
            servicio="PARTICULAR",
            estado="ACTIVO"
        )
        garantias.append(garantia)
    
    print(f"✅ Creadas {len(garantias)} garantías\n")
    
    # ========================================================================
    # CREAR EJECUCIONES ETL
    # ========================================================================
    print("🔄 Creando ejecuciones ETL...\n")
    
    estados = ['COMPLETADO', 'EN_PROGRESO', 'FALLIDO', 'INICIADO', 'PAUSADO']
    
    # Ejecución 1: Desembolso Completado
    print("  📊 Ejecución 1: Desembolso Completado")
    ejecucion1 = EjecucionETL.objects.create(
        tipo_proceso='DESEMBOLSO',
        estado='COMPLETADO',
        fecha_inicio=timezone.now() - timedelta(hours=2),
        fecha_fin=timezone.now() - timedelta(hours=1),
        total_registros=10,
        registros_procesados=10,
        registros_exitosos=10,
        registros_fallidos=0,
        ultima_etapa_ejecutada='COMPLETADO',
        descripcion='Proceso de desembolso ejecutado exitosamente'
    )
    
    # Crear procesos para ejecución 1
    for i in range(10):
        ProcesoDesembolso.objects.create(
            ejecucion=ejecucion1,
            desembolso=desembolsos[i],
            etapa_actual='COMPLETADO',
            fecha_completado=timezone.now() - timedelta(hours=1),
            intentos=1,
            datos_etapa={'exito': True, 'paso': 'final'}
        )
    
    # Ejecución 2: Desembolso En Progreso
    print("  📊 Ejecución 2: Desembolso En Progreso")
    ejecucion2 = EjecucionETL.objects.create(
        tipo_proceso='DESEMBOLSO',
        estado='EN_PROGRESO',
        fecha_inicio=timezone.now() - timedelta(minutes=30),
        total_registros=5,
        registros_procesados=3,
        registros_exitosos=2,
        registros_fallidos=1,
        ultima_etapa_ejecutada='FRACCIONAR',
        descripcion='Proceso de desembolso en ejecución'
    )
    
    # Crear procesos en diferentes etapas
    etapas_progreso = ['COMPLETADO', 'COMPLETADO', 'FRACCIONAR', 'GRABAR_CARGOS_FIJOS', 'ERROR']
    for i in range(5):
        ProcesoDesembolso.objects.create(
            ejecucion=ejecucion2,
            desembolso=desembolsos[10 + i],
            etapa_actual=etapas_progreso[i],
            fecha_completado=timezone.now() if etapas_progreso[i] == 'COMPLETADO' else None,
            intentos=2 if etapas_progreso[i] == 'ERROR' else 1,
            mensaje_error='Error al fraccionar el desembolso' if etapas_progreso[i] == 'ERROR' else None,
            datos_etapa={'etapa_actual': etapas_progreso[i]}
        )
    
    # Ejecución 3: Garantía Completada
    print("  📊 Ejecución 3: Garantía Completada")
    ejecucion3 = EjecucionETL.objects.create(
        tipo_proceso='GARANTIA',
        estado='COMPLETADO',
        fecha_inicio=timezone.now() - timedelta(days=1),
        fecha_fin=timezone.now() - timedelta(days=1) + timedelta(hours=1),
        total_registros=8,
        registros_procesados=8,
        registros_exitosos=8,
        registros_fallidos=0,
        ultima_etapa_ejecutada='COMPLETADO',
        descripcion='Proceso de garantías completado exitosamente'
    )
    
    # Crear procesos para ejecución 3
    for i in range(8):
        ProcesoGarantia.objects.create(
            ejecucion=ejecucion3,
            garantia=garantias[i],
            etapa_actual='COMPLETADO',
            fecha_completado=timezone.now() - timedelta(days=1) + timedelta(hours=1),
            intentos=1,
            datos_etapa={'exito': True, 'paso': 'final'}
        )
    
    # Ejecución 4: Garantía con Errores
    print("  📊 Ejecución 4: Garantía con Errores")
    ejecucion4 = EjecucionETL.objects.create(
        tipo_proceso='GARANTIA',
        estado='FALLIDO',
        fecha_inicio=timezone.now() - timedelta(hours=3),
        fecha_fin=timezone.now() - timedelta(hours=2),
        total_registros=5,
        registros_procesados=5,
        registros_exitosos=2,
        registros_fallidos=3,
        ultima_etapa_ejecutada='ERROR',
        descripcion='Proceso de garantías con errores',
        mensaje_error='Múltiples errores al grabar información de vehículos'
    )
    
    # Crear procesos con errores
    etapas_garantia = ['COMPLETADO', 'COMPLETADO', 'ERROR', 'ERROR', 'ERROR']
    errores = [
        None,
        None,
        'Error al validar código FASECOLDA',
        'Placa duplicada en el sistema',
        'Información de póliza incompleta'
    ]
    
    for i in range(5):
        ProcesoGarantia.objects.create(
            ejecucion=ejecucion4,
            garantia=garantias[i],
            etapa_actual=etapas_garantia[i],
            fecha_completado=timezone.now() - timedelta(hours=2) if etapas_garantia[i] == 'COMPLETADO' else None,
            intentos=3 if etapas_garantia[i] == 'ERROR' else 1,
            mensaje_error=errores[i],
            datos_etapa={
                'etapa': etapas_garantia[i],
                'detalles': errores[i] if errores[i] else 'Proceso exitoso'
            }
        )
    
    # Ejecución 5: Desembolso Iniciado
    print("  📊 Ejecución 5: Desembolso Iniciado")
    ejecucion5 = EjecucionETL.objects.create(
        tipo_proceso='DESEMBOLSO',
        estado='INICIADO',
        fecha_inicio=timezone.now() - timedelta(minutes=5),
        total_registros=3,
        registros_procesados=0,
        registros_exitosos=0,
        registros_fallidos=0,
        ultima_etapa_ejecutada='PENDIENTE',
        descripcion='Proceso recién iniciado'
    )
    
    # Crear procesos pendientes
    for i in range(3):
        if i < len(desembolsos) - 3:
            ProcesoDesembolso.objects.create(
                ejecucion=ejecucion5,
                desembolso=desembolsos[len(desembolsos) - 3 + i],
                etapa_actual='PENDIENTE',
                intentos=0
            )
    
    print("\n✅ Ejecuciones ETL creadas exitosamente")
    print("\n" + "="*60)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*60)
    print(f"  Desembolsos: {Desembolso.objects.count()}")
    print(f"  Garantías: {Garantia.objects.count()}")
    print(f"  Ejecuciones ETL: {EjecucionETL.objects.count()}")
    print(f"  Procesos Desembolso: {ProcesoDesembolso.objects.count()}")
    print(f"  Procesos Garantía: {ProcesoGarantia.objects.count()}")
    print("="*60)
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n🌐 Puedes visualizarlos en:")
    print("   - Dashboard: http://localhost:8000/dexter/")
    print("   - Ejecuciones: http://localhost:8000/dexter/ejecuciones/")
    print("\n")


if __name__ == '__main__':
    crear_datos_prueba()

