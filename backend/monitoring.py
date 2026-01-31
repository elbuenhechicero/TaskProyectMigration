"""
Sistema de monitoreo y alertas para Task Manager API
Incluye métricas de rendimiento, alertas y reportes
"""
import asyncio
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_percent: float
    disk_used: int
    disk_total: int
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    load_average: List[float]

@dataclass
class DatabaseMetrics:
    """Métricas de la base de datos"""
    timestamp: datetime
    total_documents: int
    collections_count: int
    database_size: int
    average_response_time: float
    active_connections: int
    operations_per_second: Dict[str, int]
    index_usage: Dict[str, int]

@dataclass
class ApplicationMetrics:
    """Métricas de la aplicación"""
    timestamp: datetime
    total_requests: int
    requests_per_minute: float
    average_response_time: float
    error_rate: float
    active_users: int
    cache_hit_rate: float
    cache_size: int
    endpoint_stats: Dict[str, Dict[str, any]]

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.settings = Settings()
        self.client = None
        self.metrics_history: List[SystemMetrics] = []
        self.db_metrics_history: List[DatabaseMetrics] = []
        self.app_metrics_history: List[ApplicationMetrics] = []
        
    async def connect_db(self):
        """Conectar a la base de datos"""
        if not self.client:
            self.client = AsyncIOMotorClient(self.settings.mongodb_uri)
    
    async def disconnect_db(self):
        """Desconectar de la base de datos"""
        if self.client:
            self.client.close()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Recolectar métricas del sistema"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Conexiones de red activas
        connections = len(psutil.net_connections())
        
        # Load average (Unix/Linux)
        load_avg = []
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            # Windows no tiene getloadavg
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used=memory.used,
            memory_total=memory.total,
            disk_percent=disk.percent,
            disk_used=disk.used,
            disk_total=disk.total,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            active_connections=connections,
            load_average=load_avg
        )
    
    async def collect_database_metrics(self) -> Optional[DatabaseMetrics]:
        """Recolectar métricas de la base de datos"""
        try:
            await self.connect_db()
            db = self.client[self.settings.database_name]
            
            # Contar documentos por colección
            total_docs = 0
            collections = await db.list_collection_names()
            
            for collection_name in collections:
                collection = db[collection_name]
                count = await collection.count_documents({})
                total_docs += count
            
            # Estadísticas de la base de datos
            db_stats = await db.command("dbStats")
            
            # Simular métricas adicionales (en un entorno real se obtendrían del profiler)
            metrics = DatabaseMetrics(
                timestamp=datetime.utcnow(),
                total_documents=total_docs,
                collections_count=len(collections),
                database_size=db_stats.get('dataSize', 0),
                average_response_time=0.05,  # Simulado
                active_connections=1,  # Simulado
                operations_per_second={'read': 10, 'write': 5, 'update': 3},  # Simulado
                index_usage={'users_email': 50, 'tasks_project_id': 30}  # Simulado
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error recolectando métricas de DB: {e}")
            return None
    
    async def collect_application_metrics(self) -> ApplicationMetrics:
        """Recolectar métricas de la aplicación"""
        # En un entorno real, estas métricas vendrían de la aplicación
        # Por ahora simulamos algunos valores
        
        return ApplicationMetrics(
            timestamp=datetime.utcnow(),
            total_requests=1500,  # Simulado
            requests_per_minute=25.0,  # Simulado
            average_response_time=0.15,  # Simulado
            error_rate=0.02,  # 2% de errores
            active_users=45,  # Simulado
            cache_hit_rate=0.85,  # 85% de hits
            cache_size=1024 * 1024 * 50,  # 50MB
            endpoint_stats={
                '/api/v1/tasks/': {'count': 500, 'avg_time': 0.12, 'errors': 5},
                '/api/v1/users/': {'count': 200, 'avg_time': 0.08, 'errors': 0},
                '/api/v1/projects/': {'count': 150, 'avg_time': 0.10, 'errors': 2},
                '/api/v1/dashboard/': {'count': 100, 'avg_time': 0.25, 'errors': 1}
            }
        )
    
    def store_metrics(self, metrics: SystemMetrics):
        """Almacenar métricas en historial"""
        self.metrics_history.append(metrics)
        
        # Mantener solo las últimas 1000 métricas
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def save_metrics_to_file(self, filepath: str = "logs/metrics.json"):
        """Guardar métricas en archivo JSON"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'system_metrics': [asdict(m) for m in self.metrics_history[-100:]],
                'database_metrics': [asdict(m) for m in self.db_metrics_history[-100:] if m],
                'application_metrics': [asdict(m) for m in self.app_metrics_history[-100:]],
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Convertir datetime a string para JSON
            def datetime_converter(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            with open(filepath, 'w') as f:
                json.dump(data, f, default=datetime_converter, indent=2)
                
            logger.info(f"Métricas guardadas en {filepath}")
            
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")

class AlertSystem:
    """Sistema de alertas"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 1.0,  # segundos
            'error_rate': 0.05,  # 5%
            'database_connections': 100
        }
        self.active_alerts: Dict[str, datetime] = {}
    
    def check_system_alerts(self, metrics: SystemMetrics) -> List[Dict]:
        """Verificar alertas del sistema"""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'metric': 'cpu_percent',
                'value': metrics.cpu_percent,
                'threshold': self.alert_thresholds['cpu_percent'],
                'message': f'Uso de CPU alto: {metrics.cpu_percent:.1f}%'
            })
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'metric': 'memory_percent',
                'value': metrics.memory_percent,
                'threshold': self.alert_thresholds['memory_percent'],
                'message': f'Uso de memoria alto: {metrics.memory_percent:.1f}%'
            })
        
        if metrics.disk_percent > self.alert_thresholds['disk_percent']:
            alerts.append({
                'type': 'system',
                'level': 'critical',
                'metric': 'disk_percent',
                'value': metrics.disk_percent,
                'threshold': self.alert_thresholds['disk_percent'],
                'message': f'Espacio en disco crítico: {metrics.disk_percent:.1f}%'
            })
        
        return alerts
    
    def check_application_alerts(self, metrics: ApplicationMetrics) -> List[Dict]:
        """Verificar alertas de la aplicación"""
        alerts = []
        
        if metrics.average_response_time > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'application',
                'level': 'warning',
                'metric': 'response_time',
                'value': metrics.average_response_time,
                'threshold': self.alert_thresholds['response_time'],
                'message': f'Tiempo de respuesta alto: {metrics.average_response_time:.3f}s'
            })
        
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'application',
                'level': 'warning',
                'metric': 'error_rate',
                'value': metrics.error_rate,
                'threshold': self.alert_thresholds['error_rate'],
                'message': f'Tasa de errores alta: {metrics.error_rate:.1%}'
            })
        
        return alerts
    
    def process_alerts(self, alerts: List[Dict]):
        """Procesar y registrar alertas"""
        for alert in alerts:
            alert_key = f"{alert['type']}_{alert['metric']}"
            
            # Evitar spam de alertas (una cada 5 minutos por tipo)
            if alert_key in self.active_alerts:
                time_diff = datetime.utcnow() - self.active_alerts[alert_key]
                if time_diff < timedelta(minutes=5):
                    continue
            
            # Registrar la alerta
            self.active_alerts[alert_key] = datetime.utcnow()
            
            # Log de la alerta
            level = alert['level']
            if level == 'critical':
                logger.critical(alert['message'])
            elif level == 'warning':
                logger.warning(alert['message'])
            else:
                logger.info(alert['message'])
            
            # En un entorno real, aquí se enviarían notificaciones
            # (email, Slack, SMS, etc.)

class PerformanceReporter:
    """Generador de reportes de rendimiento"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def generate_system_report(self, hours: int = 24) -> Dict:
        """Generar reporte del sistema"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.collector.metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': 'No hay datos suficientes para el reporte'}
        
        # Calcular estadísticas
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        disk_values = [m.disk_percent for m in recent_metrics]
        
        return {
            'period': f'Últimas {hours} horas',
            'sample_count': len(recent_metrics),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'disk': {
                'average': sum(disk_values) / len(disk_values),
                'max': max(disk_values),
                'min': min(disk_values)
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def generate_summary_report(self) -> Dict:
        """Generar reporte resumen"""
        if not self.collector.metrics_history:
            return {'error': 'No hay datos de métricas'}
        
        latest_system = self.collector.metrics_history[-1]
        latest_app = self.collector.app_metrics_history[-1] if self.collector.app_metrics_history else None
        latest_db = self.collector.db_metrics_history[-1] if self.collector.db_metrics_history else None
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'status': 'healthy',
                'cpu_percent': latest_system.cpu_percent,
                'memory_percent': latest_system.memory_percent,
                'disk_percent': latest_system.disk_percent,
                'active_connections': latest_system.active_connections
            }
        }
        
        if latest_app:
            report['application'] = {
                'status': 'healthy' if latest_app.error_rate < 0.05 else 'warning',
                'total_requests': latest_app.total_requests,
                'requests_per_minute': latest_app.requests_per_minute,
                'average_response_time': latest_app.average_response_time,
                'error_rate': latest_app.error_rate,
                'active_users': latest_app.active_users,
                'cache_hit_rate': latest_app.cache_hit_rate
            }
        
        if latest_db:
            report['database'] = {
                'status': 'healthy',
                'total_documents': latest_db.total_documents,
                'collections_count': latest_db.collections_count,
                'database_size': latest_db.database_size,
                'average_response_time': latest_db.average_response_time
            }
        
        return report

async def monitoring_loop():
    """Loop principal de monitoreo"""
    collector = MetricsCollector()
    alert_system = AlertSystem(collector)
    reporter = PerformanceReporter(collector)
    
    logger.info("Iniciando sistema de monitoreo...")
    
    try:
        while True:
            # Recolectar métricas del sistema
            system_metrics = collector.collect_system_metrics()
            collector.store_metrics(system_metrics)
            
            # Recolectar métricas de la base de datos
            db_metrics = await collector.collect_database_metrics()
            if db_metrics:
                collector.db_metrics_history.append(db_metrics)
            
            # Recolectar métricas de la aplicación
            app_metrics = await collector.collect_application_metrics()
            collector.app_metrics_history.append(app_metrics)
            
            # Verificar alertas
            system_alerts = alert_system.check_system_alerts(system_metrics)
            app_alerts = alert_system.check_application_alerts(app_metrics)
            
            all_alerts = system_alerts + app_alerts
            if all_alerts:
                alert_system.process_alerts(all_alerts)
            
            # Guardar métricas cada 10 iteraciones (5 minutos)
            if len(collector.metrics_history) % 10 == 0:
                collector.save_metrics_to_file()
                
                # Generar reporte resumen
                summary = reporter.generate_summary_report()
                logger.info(f"Reporte de sistema: CPU={summary['system']['cpu_percent']:.1f}%, "
                          f"Memoria={summary['system']['memory_percent']:.1f}%, "
                          f"Disco={summary['system']['disk_percent']:.1f}%")
            
            # Esperar 30 segundos antes de la siguiente recolección
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        logger.info("Monitoreo detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el loop de monitoreo: {e}")
    finally:
        await collector.disconnect_db()

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar monitoreo
    asyncio.run(monitoring_loop())