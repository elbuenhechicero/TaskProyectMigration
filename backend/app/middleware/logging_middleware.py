"""
Middleware para logging, métricas y monitoreo de requests
"""
import time
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class RequestMetrics:
    """Almacén de métricas de requests"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.requests_history: deque = deque(maxlen=max_history)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'errors': 0,
            'last_accessed': None
        })
        self.active_requests = 0
        self.lock = threading.Lock()
    
    def record_request(self, method: str, path: str, duration: float, 
                      status_code: int, user_id: Optional[str] = None):
        """Registrar una request"""
        with self.lock:
            timestamp = datetime.utcnow()
            
            # Registrar en historial
            request_data = {
                'timestamp': timestamp,
                'method': method,
                'path': path,
                'duration': duration,
                'status_code': status_code,
                'user_id': user_id,
                'is_error': status_code >= 400
            }
            self.requests_history.append(request_data)
            
            # Actualizar estadísticas por endpoint
            endpoint_key = f"{method} {path}"
            stats = self.endpoint_stats[endpoint_key]
            stats['count'] += 1
            stats['total_time'] += duration
            stats['last_accessed'] = timestamp
            
            if status_code >= 400:
                stats['errors'] += 1
    
    def get_stats(self, minutes: int = 5) -> Dict:
        """Obtener estadísticas de los últimos N minutos"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            recent_requests = [
                req for req in self.requests_history
                if req['timestamp'] >= cutoff_time
            ]
            
            if not recent_requests:
                return {
                    'total_requests': 0,
                    'requests_per_minute': 0.0,
                    'average_response_time': 0.0,
                    'error_rate': 0.0,
                    'status_codes': {},
                    'top_endpoints': []
                }
            
            # Calcular métricas
            total_requests = len(recent_requests)
            total_errors = sum(1 for req in recent_requests if req['is_error'])
            total_time = sum(req['duration'] for req in recent_requests)
            
            # Contar códigos de estado
            status_codes = defaultdict(int)
            for req in recent_requests:
                status_codes[req['status_code']] += 1
            
            # Top endpoints
            endpoint_counts = defaultdict(int)
            endpoint_times = defaultdict(list)
            for req in recent_requests:
                endpoint = f"{req['method']} {req['path']}"
                endpoint_counts[endpoint] += 1
                endpoint_times[endpoint].append(req['duration'])
            
            top_endpoints = []
            for endpoint, count in sorted(endpoint_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]:
                avg_time = sum(endpoint_times[endpoint]) / len(endpoint_times[endpoint])
                top_endpoints.append({
                    'endpoint': endpoint,
                    'count': count,
                    'avg_response_time': avg_time
                })
            
            return {
                'period_minutes': minutes,
                'total_requests': total_requests,
                'requests_per_minute': total_requests / minutes,
                'average_response_time': total_time / total_requests if total_requests > 0 else 0,
                'error_rate': total_errors / total_requests if total_requests > 0 else 0,
                'active_requests': self.active_requests,
                'status_codes': dict(status_codes),
                'top_endpoints': top_endpoints
            }
    
    def get_endpoint_stats(self) -> Dict:
        """Obtener estadísticas por endpoint"""
        with self.lock:
            stats = {}
            for endpoint, data in self.endpoint_stats.items():
                if data['count'] > 0:
                    stats[endpoint] = {
                        'count': data['count'],
                        'avg_response_time': data['total_time'] / data['count'],
                        'errors': data['errors'],
                        'error_rate': data['errors'] / data['count'],
                        'last_accessed': data['last_accessed'].isoformat() if data['last_accessed'] else None
                    }
            return stats

# Instancia global de métricas
request_metrics = RequestMetrics()

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging detallado de requests"""
    
    def __init__(self, app, log_body: bool = False, sensitive_headers: List[str] = None):
        super().__init__(app)
        self.log_body = log_body
        self.sensitive_headers = sensitive_headers or [
            'authorization', 'cookie', 'x-api-key'
        ]
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extraer información de la request
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        user_id = None
        
        # Intentar extraer user_id del token JWT si existe
        try:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                # Aquí podrías decodificar el token para obtener el user_id
                # Por simplicidad, lo omitimos
                pass
        except:
            pass
        
        # Incrementar requests activos
        request_metrics.active_requests += 1
        
        # Log de request entrante
        logger.info(f"Request started: {request.method} {request.url.path} "
                   f"from {client_ip} ({user_agent[:50]})")
        
        # Loggear headers (excluyendo los sensibles)
        filtered_headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in self.sensitive_headers
        }
        logger.debug(f"Request headers: {filtered_headers}")
        
        # Loggear body si está habilitado (solo para métodos que lo tengan)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Leer el body sin consumirlo
                body = await request.body()
                if body:
                    # Intentar parsear como JSON para mejor formato
                    try:
                        body_json = json.loads(body.decode())
                        # Filtrar campos sensibles
                        if isinstance(body_json, dict):
                            filtered_body = {
                                k: "***HIDDEN***" if k.lower() in ['password', 'secret', 'token'] else v
                                for k, v in body_json.items()
                            }
                            logger.debug(f"Request body: {json.dumps(filtered_body, indent=2)}")
                    except:
                        # Si no es JSON válido, loggear como string truncado
                        body_str = body.decode()[:500]
                        logger.debug(f"Request body (text): {body_str}")
            except Exception as e:
                logger.debug(f"Could not read request body: {e}")
        
        try:
            # Procesar la request
            response = await call_next(request)
            
            # Calcular duración
            duration = time.time() - start_time
            
            # Log de respuesta
            logger.info(f"Request completed: {request.method} {request.url.path} "
                       f"-> {response.status_code} in {duration:.3f}s")
            
            # Registrar métricas
            request_metrics.record_request(
                method=request.method,
                path=request.url.path,
                duration=duration,
                status_code=response.status_code,
                user_id=user_id
            )
            
            # Agregar headers de información
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Request-ID"] = str(time.time())
            
            return response
            
        except Exception as e:
            # Log de error
            duration = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} "
                        f"in {duration:.3f}s - Error: {str(e)}")
            
            # Registrar métricas de error
            request_metrics.record_request(
                method=request.method,
                path=request.url.path,
                duration=duration,
                status_code=500,
                user_id=user_id
            )
            
            raise
        finally:
            # Decrementar requests activos
            request_metrics.active_requests -= 1

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Agregar headers de seguridad
        for header, value in self.security_headers.items():
            if header not in response.headers:
                response.headers[header] = value
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware básico para rate limiting"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, deque] = defaultdict(lambda: deque())
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Limpiar requests antiguas (más de 1 minuto)
        client_requests = self.clients[client_ip]
        while client_requests and now - client_requests[0] > 60:
            client_requests.popleft()
        
        # Verificar límite
        if len(client_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute"
                }
            )
        
        # Registrar request
        client_requests.append(now)
        
        response = await call_next(request)
        
        # Agregar headers informativos
        remaining = self.requests_per_minute - len(client_requests)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        
        return response

# Funciones utilitarias para obtener métricas
def get_request_metrics(minutes: int = 5) -> Dict:
    """Obtener métricas de requests"""
    return request_metrics.get_stats(minutes)

def get_endpoint_stats() -> Dict:
    """Obtener estadísticas por endpoint"""
    return request_metrics.get_endpoint_stats()

def get_active_requests_count() -> int:
    """Obtener número de requests activos"""
    return request_metrics.active_requests