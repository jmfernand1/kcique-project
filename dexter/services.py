"""
Servicios de negocio para el sistema de tracking ETL.
Encapsula toda la lógica de negocio relacionada con ejecuciones y procesos.
"""

from django.utils import timezone
from django.db import transaction
from typing import List, Optional, Dict, Any
from .models import (
    EjecucionETL,
    ProcesoDesembolso,
    ProcesoGarantia,
    EtapaProcesoDesembolso,
    EtapaProcesoGarantia,
    Desembolso,
    Garantia,
    TipoDesembolso,
    TipoGarantia,
    EtapaTipoDesembolso,
    EtapaTipoGarantia,
)


class EjecucionETLService:
    """Servicio para gestionar ejecuciones ETL"""
    
    @staticmethod
    @transaction.atomic
    def crear_ejecucion_con_plan(
        tipo_proceso: str,
        total_registros: int,
        descripcion: str = None,
        desembolsos: List[Desembolso] = None,
        garantias: List[Garantia] = None
    ) -> EjecucionETL:
        """
        Crea una ejecución ETL y su plan de ejecución completo.
        
        Args:
            tipo_proceso: 'DESEMBOLSO' o 'GARANTIA'
            total_registros: Total de registros a procesar
            descripcion: Descripción opcional
            desembolsos: Lista de desembolsos (si tipo_proceso='DESEMBOLSO')
            garantias: Lista de garantías (si tipo_proceso='GARANTIA')
        
        Returns:
            EjecucionETL creada
        """
        # Crear ejecución
        ejecucion = EjecucionETL.objects.create(
            tipo_proceso=tipo_proceso,
            estado='INICIADO',
            total_registros=total_registros,
            descripcion=descripcion or f'ETL {tipo_proceso} - {timezone.now()}'
        )
        
        # Crear plan de ejecución
        if tipo_proceso == 'DESEMBOLSO' and desembolsos:
            ProcesoDesembolsoService.crear_plan_ejecucion(ejecucion, desembolsos)
        elif tipo_proceso == 'GARANTIA' and garantias:
            ProcesoGarantiaService.crear_plan_ejecucion(ejecucion, garantias)
        
        ejecucion.estado = 'EN_PROGRESO'
        ejecucion.save()
        
        return ejecucion
    
    @staticmethod
    def obtener_ejecuciones_pendientes(tipo_proceso: str = None) -> List[EjecucionETL]:
        """Obtiene ejecuciones que pueden ser retomadas"""
        queryset = EjecucionETL.objects.filter(
            estado__in=['INICIADO', 'EN_PROGRESO', 'PAUSADO', 'FALLIDO']
        )
        if tipo_proceso:
            queryset = queryset.filter(tipo_proceso=tipo_proceso)
        return list(queryset.order_by('-fecha_inicio'))
    
    @staticmethod
    def retomar_ejecucion(ejecucion_id: int) -> EjecucionETL:
        """Retoma una ejecución pausada o fallida"""
        ejecucion = EjecucionETL.objects.get(id=ejecucion_id)
        if ejecucion.estado in ['PAUSADO', 'FALLIDO']:
            ejecucion.estado = 'EN_PROGRESO'
            ejecucion.save()
        return ejecucion
    
    @staticmethod
    def completar_ejecucion(ejecucion_id: int) -> EjecucionETL:
        """Marca una ejecución como completada"""
        ejecucion = EjecucionETL.objects.get(id=ejecucion_id)
        ejecucion.estado = 'COMPLETADO'
        ejecucion.fecha_fin = timezone.now()
        ejecucion.save()
        return ejecucion
    
    @staticmethod
    def fallar_ejecucion(ejecucion_id: int, mensaje_error: str = None) -> EjecucionETL:
        """Marca una ejecución como fallida"""
        ejecucion = EjecucionETL.objects.get(id=ejecucion_id)
        ejecucion.estado = 'FALLIDO'
        ejecucion.fecha_fin = timezone.now()
        if mensaje_error:
            ejecucion.mensaje_error = mensaje_error
        ejecucion.save()
        return ejecucion


class ProcesoDesembolsoService:
    """Servicio para gestionar procesos de desembolso"""
    
    @staticmethod
    @transaction.atomic
    def crear_plan_ejecucion(
        ejecucion: EjecucionETL,
        desembolsos: List[Desembolso]
    ) -> List[ProcesoDesembolso]:
        """
        Crea el plan de ejecución completo para una lista de desembolsos.
        Crea un ProcesoDesembolso y todas sus EtapaProcesoDesembolso.
        
        Args:
            ejecucion: Ejecución ETL
            desembolsos: Lista de desembolsos a procesar
        
        Returns:
            Lista de ProcesoDesembolso creados
        """
        procesos_creados = []
        
        for desembolso in desembolsos:
            # Obtener tipo de desembolso
            tipo_desembolso = desembolso.tipo_desembolso
            if not tipo_desembolso:
                raise ValueError(
                    f"El desembolso {desembolso.referencia} no tiene tipo_desembolso asignado"
                )
            
            # Obtener etapas del tipo de desembolso ordenadas
            etapas_tipo = EtapaTipoDesembolso.objects.filter(
                tipo_desembolso=tipo_desembolso
            ).order_by('orden')
            
            if not etapas_tipo.exists():
                raise ValueError(
                    f"El tipo de desembolso {tipo_desembolso.nombre} no tiene etapas configuradas"
                )
            
            # Crear proceso principal
            proceso = ProcesoDesembolso.objects.create(
                ejecucion=ejecucion,
                desembolso=desembolso,
                estado_general='PENDIENTE'
            )
            
            # Crear todas las etapas del plan
            for etapa_tipo in etapas_tipo:
                EtapaProcesoDesembolso.objects.create(
                    proceso=proceso,
                    etapa=etapa_tipo,
                    orden=etapa_tipo.orden,
                    estado='PENDIENTE'
                )
            
            procesos_creados.append(proceso)
        
        return procesos_creados
    
    @staticmethod
    def obtener_procesos_pendientes(
        ejecucion_id: int,
        estado_general: str = None
    ) -> List[ProcesoDesembolso]:
        """
        Obtiene procesos pendientes de una ejecución.
        Útil para retomar una ejecución fallida.
        """
        queryset = ProcesoDesembolso.objects.filter(
            ejecucion_id=ejecucion_id
        ).prefetch_related('etapas__etapa')
        
        if estado_general:
            queryset = queryset.filter(estado_general=estado_general)
        else:
            queryset = queryset.exclude(estado_general='COMPLETADO')
        
        return list(queryset.order_by('id'))
    
    @staticmethod
    def obtener_siguiente_etapa(proceso_id: int) -> Optional[EtapaProcesoDesembolso]:
        """
        Obtiene la siguiente etapa pendiente de un proceso.
        Retorna None si todas las etapas están completadas.
        """
        proceso = ProcesoDesembolso.objects.prefetch_related('etapas__etapa').get(
            id=proceso_id
        )
        return proceso.siguiente_etapa
    
    @staticmethod
    @transaction.atomic
    def iniciar_etapa(etapa_proceso_id: int) -> EtapaProcesoDesembolso:
        """
        Inicia una etapa específica.
        La marca como EN_PROGRESO y actualiza el proceso.
        """
        etapa_proceso = EtapaProcesoDesembolso.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        etapa_proceso.iniciar()
        
        # Actualizar estado del proceso
        proceso = etapa_proceso.proceso
        if proceso.estado_general == 'PENDIENTE':
            proceso.estado_general = 'EN_PROGRESO'
            proceso.save()
        
        return etapa_proceso
    
    @staticmethod
    @transaction.atomic
    def completar_etapa(
        etapa_proceso_id: int,
        datos_etapa: Dict[str, Any] = None
    ) -> EtapaProcesoDesembolso:
        """
        Completa una etapa específica.
        Avanza automáticamente a la siguiente etapa si existe.
        """
        etapa_proceso = EtapaProcesoDesembolso.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        etapa_proceso.completar(datos_etapa=datos_etapa)
        
        # Actualizar contadores de la ejecución
        proceso = etapa_proceso.proceso
        ejecucion = proceso.ejecucion
        
        # Solo incrementar si es la última etapa completada
        if proceso.marcar_como_completado():
            ejecucion.registros_procesados += 1
            ejecucion.registros_exitosos += 1
            ejecucion.save()
        
        return etapa_proceso
    
    @staticmethod
    @transaction.atomic
    def marcar_error_etapa(
        etapa_proceso_id: int,
        mensaje_error: str,
        datos_etapa: Dict[str, Any] = None
    ) -> EtapaProcesoDesembolso:
        """
        Marca una etapa como error.
        No avanza a la siguiente etapa.
        """
        etapa_proceso = EtapaProcesoDesembolso.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        etapa_proceso.marcar_error(mensaje_error, datos_etapa=datos_etapa)
        
        # Actualizar contador de errores de la ejecución
        ejecucion = etapa_proceso.proceso.ejecucion
        ejecucion.registros_fallidos += 1
        ejecucion.save()
        
        return etapa_proceso
    
    @staticmethod
    @transaction.atomic
    def reintentar_etapa(etapa_proceso_id: int) -> EtapaProcesoDesembolso:
        """
        Reintenta una etapa que falló.
        Limpia el error y la marca como EN_PROGRESO nuevamente.
        """
        etapa_proceso = EtapaProcesoDesembolso.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        if etapa_proceso.estado != 'ERROR':
            raise ValueError("Solo se pueden reintentar etapas con estado ERROR")
        
        etapa_proceso.estado = 'EN_PROGRESO'
        etapa_proceso.mensaje_error = None
        etapa_proceso.fecha_inicio = timezone.now()
        etapa_proceso.intentos += 1
        etapa_proceso.save()
        
        # Actualizar estado del proceso
        proceso = etapa_proceso.proceso
        proceso.estado_general = 'EN_PROGRESO'
        proceso.save()
        
        return etapa_proceso


class ProcesoGarantiaService:
    """Servicio para gestionar procesos de garantía"""
    
    @staticmethod
    @transaction.atomic
    def crear_plan_ejecucion(
        ejecucion: EjecucionETL,
        garantias: List[Garantia]
    ) -> List[ProcesoGarantia]:
        """
        Crea el plan de ejecución completo para una lista de garantías.
        Crea un ProcesoGarantia y todas sus EtapaProcesoGarantia.
        
        Args:
            ejecucion: Ejecución ETL
            garantias: Lista de garantías a procesar
        
        Returns:
            Lista de ProcesoGarantia creados
        """
        procesos_creados = []
        
        # Obtener tipo de garantía por defecto (puedes ajustar esta lógica)
        tipo_garantia = TipoGarantia.objects.first()
        if not tipo_garantia:
            raise ValueError("No hay tipos de garantía configurados")
        
        # Obtener etapas del tipo de garantía ordenadas
        etapas_tipo = EtapaTipoGarantia.objects.filter(
            tipo_garantia=tipo_garantia
        ).order_by('orden')
        
        if not etapas_tipo.exists():
            raise ValueError(
                f"El tipo de garantía {tipo_garantia.nombre} no tiene etapas configuradas"
            )
        
        for garantia in garantias:
            # Crear proceso principal
            proceso = ProcesoGarantia.objects.create(
                ejecucion=ejecucion,
                garantia=garantia,
                estado_general='PENDIENTE'
            )
            
            # Crear todas las etapas del plan
            for etapa_tipo in etapas_tipo:
                EtapaProcesoGarantia.objects.create(
                    proceso=proceso,
                    etapa=etapa_tipo,
                    orden=etapa_tipo.orden,
                    estado='PENDIENTE'
                )
            
            procesos_creados.append(proceso)
        
        return procesos_creados
    
    @staticmethod
    def obtener_procesos_pendientes(
        ejecucion_id: int,
        estado_general: str = None
    ) -> List[ProcesoGarantia]:
        """
        Obtiene procesos pendientes de una ejecución.
        Útil para retomar una ejecución fallida.
        """
        queryset = ProcesoGarantia.objects.filter(
            ejecucion_id=ejecucion_id
        ).prefetch_related('etapas__etapa')
        
        if estado_general:
            queryset = queryset.filter(estado_general=estado_general)
        else:
            queryset = queryset.exclude(estado_general='COMPLETADO')
        
        return list(queryset.order_by('id'))
    
    @staticmethod
    def obtener_siguiente_etapa(proceso_id: int) -> Optional[EtapaProcesoGarantia]:
        """
        Obtiene la siguiente etapa pendiente de un proceso.
        Retorna None si todas las etapas están completadas.
        """
        proceso = ProcesoGarantia.objects.prefetch_related('etapas__etapa').get(
            id=proceso_id
        )
        return proceso.siguiente_etapa
    
    @staticmethod
    @transaction.atomic
    def iniciar_etapa(etapa_proceso_id: int) -> EtapaProcesoGarantia:
        """
        Inicia una etapa específica.
        La marca como EN_PROGRESO y actualiza el proceso.
        """
        etapa_proceso = EtapaProcesoGarantia.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        etapa_proceso.iniciar()
        
        # Actualizar estado del proceso
        proceso = etapa_proceso.proceso
        if proceso.estado_general == 'PENDIENTE':
            proceso.estado_general = 'EN_PROGRESO'
            proceso.save()
        
        return etapa_proceso
    
    @staticmethod
    @transaction.atomic
    def completar_etapa(
        etapa_proceso_id: int,
        datos_etapa: Dict[str, Any] = None
    ) -> EtapaProcesoGarantia:
        """
        Completa una etapa específica.
        Avanza automáticamente a la siguiente etapa si existe.
        """
        etapa_proceso = EtapaProcesoGarantia.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        etapa_proceso.completar(datos_etapa=datos_etapa)
        
        # Actualizar contadores de la ejecución
        proceso = etapa_proceso.proceso
        ejecucion = proceso.ejecucion
        
        # Solo incrementar si es la última etapa completada
        if proceso.marcar_como_completado():
            ejecucion.registros_procesados += 1
            ejecucion.registros_exitosos += 1
            ejecucion.save()
        
        return etapa_proceso
    
    @staticmethod
    @transaction.atomic
    def marcar_error_etapa(
        etapa_proceso_id: int,
        mensaje_error: str,
        datos_etapa: Dict[str, Any] = None
    ) -> EtapaProcesoGarantia:
        """
        Marca una etapa como error.
        No avanza a la siguiente etapa.
        """
        etapa_proceso = EtapaProcesoGarantia.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        etapa_proceso.marcar_error(mensaje_error, datos_etapa=datos_etapa)
        
        # Actualizar contador de errores de la ejecución
        ejecucion = etapa_proceso.proceso.ejecucion
        ejecucion.registros_fallidos += 1
        ejecucion.save()
        
        return etapa_proceso
    
    @staticmethod
    @transaction.atomic
    def reintentar_etapa(etapa_proceso_id: int) -> EtapaProcesoGarantia:
        """
        Reintenta una etapa que falló.
        Limpia el error y la marca como EN_PROGRESO nuevamente.
        """
        etapa_proceso = EtapaProcesoGarantia.objects.select_related(
            'proceso', 'etapa'
        ).get(id=etapa_proceso_id)
        
        if etapa_proceso.estado != 'ERROR':
            raise ValueError("Solo se pueden reintentar etapas con estado ERROR")
        
        etapa_proceso.estado = 'EN_PROGRESO'
        etapa_proceso.mensaje_error = None
        etapa_proceso.fecha_inicio = timezone.now()
        etapa_proceso.intentos += 1
        etapa_proceso.save()
        
        # Actualizar estado del proceso
        proceso = etapa_proceso.proceso
        proceso.estado_general = 'EN_PROGRESO'
        proceso.save()
        
        return etapa_proceso

