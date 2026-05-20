#!/usr/bin/env python
"""
Script de verificación para la API de Dexter

Este script verifica que todos los componentes de Dexter estén correctamente configurados.
Ejecutar antes de iniciar el servidor Django.

Uso:
    python verificar_dexter.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kcique_project.settings')
django.setup()

from django.core.management import call_command
from django.apps import apps
from django.urls import get_resolver
from dexter.models import Desembolso, CargoFijo, Garantia


def print_header(texto):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70)


def verificar_app_instalada():
    """Verifica que la app dexter esté instalada"""
    print_header("1. Verificando que Dexter esté instalada")
    
    try:
        app_config = apps.get_app_config('dexter')
        print(f"✅ App 'dexter' encontrada")
        print(f"   - Nombre: {app_config.name}")
        print(f"   - Verbose Name: {app_config.verbose_name}")
        return True
    except LookupError:
        print("❌ App 'dexter' NO encontrada en INSTALLED_APPS")
        return False


def verificar_modelos():
    """Verifica que los modelos estén correctamente configurados"""
    print_header("2. Verificando Modelos")
    
    modelos = [
        ('Desembolso', Desembolso),
        ('CargoFijo', CargoFijo),
        ('Garantia', Garantia)
    ]
    
    todos_ok = True
    for nombre, modelo in modelos:
        try:
            # Verificar que la tabla existe
            count = modelo.objects.count()
            print(f"✅ Modelo '{nombre}' OK - {count} registros en DB")
        except Exception as e:
            print(f"❌ Error en modelo '{nombre}': {e}")
            todos_ok = False
    
    return todos_ok


def verificar_migraciones():
    """Verifica el estado de las migraciones"""
    print_header("3. Verificando Migraciones")
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print("⚠️  Hay migraciones pendientes:")
            for migration, backwards in plan:
                print(f"   - {migration}")
            print("\n   Ejecuta: python manage.py migrate")
            return False
        else:
            print("✅ Todas las migraciones están aplicadas")
            return True
    except Exception as e:
        print(f"❌ Error verificando migraciones: {e}")
        return False


def verificar_urls():
    """Verifica que las URLs estén configuradas"""
    print_header("4. Verificando URLs")
    
    try:
        resolver = get_resolver()
        
        # Buscar URLs de dexter
        dexter_urls = []
        for pattern in resolver.url_patterns:
            pattern_str = str(pattern.pattern)
            if 'dexter' in pattern_str:
                dexter_urls.append(pattern_str)
        
        if dexter_urls:
            print("✅ URLs de Dexter encontradas:")
            for url in dexter_urls:
                print(f"   - {url}")
            return True
        else:
            print("❌ No se encontraron URLs de Dexter")
            print("   Verifica que 'dexter.urls' esté incluido en urls.py principal")
            return False
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False


def verificar_serializers():
    """Verifica que los serializers estén configurados"""
    print_header("5. Verificando Serializers")
    
    try:
        from dexter.serializers import (
            DesembolsoSerializer,
            DesembolsoWriteSerializer,
            CargoFijoSerializer,
            GarantiaSerializer
        )
        
        serializers = [
            'DesembolsoSerializer',
            'DesembolsoWriteSerializer',
            'CargoFijoSerializer',
            'GarantiaSerializer'
        ]
        
        print("✅ Todos los serializers encontrados:")
        for serializer in serializers:
            print(f"   - {serializer}")
        return True
    except ImportError as e:
        print(f"❌ Error importando serializers: {e}")
        return False


def verificar_viewsets():
    """Verifica que los ViewSets estén configurados"""
    print_header("6. Verificando ViewSets")
    
    try:
        from dexter.views import (
            DesembolsoViewSet,
            CargoFijoViewSet,
            GarantiaViewSet
        )
        
        viewsets = [
            ('DesembolsoViewSet', DesembolsoViewSet),
            ('CargoFijoViewSet', CargoFijoViewSet),
            ('GarantiaViewSet', GarantiaViewSet)
        ]
        
        print("✅ Todos los ViewSets encontrados:")
        for nombre, viewset in viewsets:
            print(f"   - {nombre}")
            print(f"     Modelo: {viewset.queryset.model.__name__}")
            print(f"     Filtros: {viewset.filterset_fields if hasattr(viewset, 'filterset_fields') else 'N/A'}")
        return True
    except ImportError as e:
        print(f"❌ Error importando ViewSets: {e}")
        return False


def verificar_admin():
    """Verifica que los modelos estén registrados en el admin"""
    print_header("7. Verificando Admin")
    
    try:
        from django.contrib import admin
        
        modelos_admin = [
            ('Desembolso', Desembolso),
            ('CargoFijo', CargoFijo),
            ('Garantia', Garantia)
        ]
        
        todos_ok = True
        for nombre, modelo in modelos_admin:
            if admin.site.is_registered(modelo):
                admin_class = admin.site._registry[modelo]
                print(f"✅ {nombre} registrado en Admin")
                print(f"   - Clase: {admin_class.__class__.__name__}")
            else:
                print(f"❌ {nombre} NO registrado en Admin")
                todos_ok = False
        
        return todos_ok
    except Exception as e:
        print(f"❌ Error verificando Admin: {e}")
        return False


def verificar_archivos():
    """Verifica que los archivos necesarios existan"""
    print_header("8. Verificando Archivos")
    
    archivos_necesarios = [
        'dexter/models.py',
        'dexter/serializers.py',
        'dexter/views.py',
        'dexter/urls.py',
        'dexter/admin.py',
        'dexter/README.md',
        'dexter/ejemplo_uso_api.py',
    ]
    
    todos_ok = True
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} NO encontrado")
            todos_ok = False
    
    return todos_ok


def test_creacion_basica():
    """Prueba crear un registro básico"""
    print_header("9. Prueba de Creación Básica")
    
    try:
        # Intentar crear un desembolso de prueba
        desembolso = Desembolso(
            referencia="TEST-VERIFICACION-001",
            obligacion=999999999,
            id_cliente=888888888,
            nit_beneficiario=900999999,
            aliado="TEST",
            tipo_cta_destino="Test",
            cod_tipo_cuenta_destino=1,
            num_cta_destino=1111111111,
            banco_destino="Test",
            cod_banco_destino=99,
            valor_desembolso=1000.00,
            numero_tramos=1,
            plazo_tramo_1=12,
            tipo_tasa_tramo_1="EA",
            tasa_tramo_1=15.0,
            amortizacion_tramo_1="TEST",
            plazo_tramo_2=0,
            tipo_tasa_tramo_2="EA",
            tasa_tramo_2=0.0,
            amortizacion_tramo_2="TEST"
        )
        desembolso.save()
        print(f"✅ Desembolso de prueba creado (ID: {desembolso.id})")
        
        # Limpiar
        desembolso.delete()
        print("✅ Desembolso de prueba eliminado")
        
        return True
    except Exception as e:
        print(f"❌ Error en prueba de creación: {e}")
        return False


def main():
    """Función principal"""
    print("\n" + "🚀" * 35)
    print("     VERIFICACIÓN DE LA API DE DEXTER")
    print("🚀" * 35)
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(("App Instalada", verificar_app_instalada()))
    resultados.append(("Modelos", verificar_modelos()))
    resultados.append(("Migraciones", verificar_migraciones()))
    resultados.append(("URLs", verificar_urls()))
    resultados.append(("Serializers", verificar_serializers()))
    resultados.append(("ViewSets", verificar_viewsets()))
    resultados.append(("Admin", verificar_admin()))
    resultados.append(("Archivos", verificar_archivos()))
    resultados.append(("Prueba Creación", test_creacion_basica()))
    
    # Resumen
    print_header("RESUMEN DE VERIFICACIÓN")
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        simbolo = "✅" if resultado else "❌"
        print(f"{simbolo} {nombre}")
    
    print(f"\n{'=' * 70}")
    print(f"  Total: {exitosos}/{total} verificaciones exitosas")
    print(f"{'=' * 70}")
    
    if exitosos == total:
        print("\n🎉 ¡TODO ESTÁ CORRECTO! La API de Dexter está lista para usar.")
        print("\nPróximos pasos:")
        print("  1. Inicia el servidor: python manage.py runserver")
        print("  2. Accede a: http://localhost:8000/dexter/api/")
        print("  3. Prueba el cliente: python dexter/ejemplo_uso_api.py")
        return 0
    else:
        print("\n⚠️  Hay algunas verificaciones que fallaron.")
        print("   Revisa los errores arriba y corrígelos antes de continuar.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

