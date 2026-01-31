"""
Modelos para Dashboard y Reportes
Sistema de estadísticas y métricas del proyecto
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from enum import Enum

class ReportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"

class TimeRange(str, Enum):
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"

class MetricType(str, Enum):
    TASKS = "tasks"
    PROJECTS = "projects"
    USERS = "users"
    COMMENTS = "comments"
    PRODUCTIVITY = "productivity"

# Modelos para estadísticas generales
class TaskStatistics(BaseModel):
    """Estadísticas de tareas"""
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: float = 0.0
    average_completion_time: Optional[float] = None  # en días
    
    # Estadísticas por prioridad
    high_priority_tasks: int = 0
    medium_priority_tasks: int = 0
    low_priority_tasks: int = 0
    
    # Estadísticas por fecha
    tasks_created_this_week: int = 0
    tasks_completed_this_week: int = 0
    tasks_created_this_month: int = 0
    tasks_completed_this_month: int = 0

class ProjectStatistics(BaseModel):
    """Estadísticas de proyectos"""
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    overdue_projects: int = 0
    average_tasks_per_project: float = 0.0
    average_project_completion_time: Optional[float] = None  # en días
    
    # Proyectos más activos
    most_active_project: Optional[str] = None
    most_active_project_tasks: int = 0

class UserStatistics(BaseModel):
    """Estadísticas de usuarios"""
    total_users: int = 0
    active_users: int = 0  # usuarios con actividad en los últimos 30 días
    most_productive_user: Optional[str] = None
    most_productive_user_tasks: int = 0
    
    # Estadísticas de colaboración
    average_tasks_per_user: float = 0.0
    users_with_overdue_tasks: int = 0

class ProductivityMetrics(BaseModel):
    """Métricas de productividad"""
    tasks_completed_today: int = 0
    tasks_completed_this_week: int = 0
    tasks_completed_this_month: int = 0
    
    # Tendencias
    completion_trend_7_days: List[int] = []  # tareas completadas por día
    creation_trend_7_days: List[int] = []   # tareas creadas por día
    
    # Tiempo promedio de finalización
    average_task_duration: Optional[float] = None  # en horas
    median_task_duration: Optional[float] = None   # en horas
    
    # Eficiencia
    on_time_completion_rate: float = 0.0
    early_completion_rate: float = 0.0
    late_completion_rate: float = 0.0

class DashboardSummary(BaseModel):
    """Resumen completo del dashboard"""
    task_stats: TaskStatistics
    project_stats: ProjectStatistics
    user_stats: UserStatistics
    productivity_metrics: ProductivityMetrics
    
    # Metadatos
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_range: TimeRange = TimeRange.LAST_30_DAYS
    
    # Alertas y notificaciones importantes
    alerts: List[str] = []
    recommendations: List[str] = []

# Modelos para reportes específicos
class TaskReport(BaseModel):
    """Reporte detallado de tareas"""
    id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    project_name: Optional[str] = None
    assigned_username: Optional[str] = None
    created_username: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[date] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    completion_time_days: Optional[float] = None  # días para completar
    is_overdue: bool = False
    comments_count: int = 0

class ProjectReport(BaseModel):
    """Reporte detallado de proyectos"""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    created_username: str
    created_at: datetime
    updated_at: datetime
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_overdue: bool = False
    
    # Estadísticas del proyecto
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    completion_rate: float = 0.0
    assigned_users: List[str] = []

class UserProductivityReport(BaseModel):
    """Reporte de productividad de usuarios"""
    user_id: str
    username: str
    email: str
    
    # Estadísticas de tareas
    assigned_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: float = 0.0
    
    # Métricas de tiempo
    average_completion_time: Optional[float] = None  # días
    total_estimated_hours: float = 0.0
    total_actual_hours: float = 0.0
    time_accuracy: float = 0.0  # qué tan preciso es estimando tiempo
    
    # Actividad reciente
    tasks_created_this_month: int = 0
    tasks_completed_this_month: int = 0
    comments_this_month: int = 0
    
    # Proyectos involucrados
    active_projects: List[str] = []

# Modelos para filtros de reportes
class ReportFilters(BaseModel):
    """Filtros para generar reportes"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_ids: Optional[List[str]] = []
    user_ids: Optional[List[str]] = []
    task_statuses: Optional[List[str]] = []
    task_priorities: Optional[List[str]] = []
    include_completed: bool = True
    include_overdue_only: bool = False
    
class ReportRequest(BaseModel):
    """Solicitud para generar reporte"""
    report_type: MetricType
    format: ReportFormat = ReportFormat.JSON
    filters: Optional[ReportFilters] = None
    time_range: TimeRange = TimeRange.LAST_30_DAYS
    custom_start_date: Optional[date] = None
    custom_end_date: Optional[date] = None
    
    # Opciones específicas del reporte
    include_charts: bool = False
    include_details: bool = True
    group_by: Optional[str] = None  # "project", "user", "status", "priority"

class ReportResponse(BaseModel):
    """Respuesta de reporte generado"""
    report_id: str
    report_type: MetricType
    format: ReportFormat
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    filters_applied: Optional[ReportFilters] = None
    
    # Datos del reporte
    summary: Dict[str, Any] = {}
    data: List[Dict[str, Any]] = []
    charts: Optional[Dict[str, Any]] = None
    
    # Metadatos
    total_records: int = 0
    execution_time_ms: Optional[float] = None
    
    # Para reportes exportados
    download_url: Optional[str] = None
    file_size: Optional[int] = None

# Modelos para gráficos y visualizaciones
class ChartDataPoint(BaseModel):
    """Punto de datos para gráficos"""
    label: str
    value: float
    date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = {}

class ChartData(BaseModel):
    """Datos para gráficos"""
    chart_type: str  # "line", "bar", "pie", "area"
    title: str
    x_axis_label: str = ""
    y_axis_label: str = ""
    data_points: List[ChartDataPoint] = []
    colors: Optional[List[str]] = []
    
class DashboardWidget(BaseModel):
    """Widget del dashboard"""
    widget_id: str
    title: str
    widget_type: str  # "metric", "chart", "table", "alert"
    data: Dict[str, Any] = {}
    position: Dict[str, int] = {"x": 0, "y": 0, "width": 1, "height": 1}
    refresh_interval: int = 300  # segundos
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class DashboardLayout(BaseModel):
    """Layout completo del dashboard"""
    user_id: str
    layout_name: str = "default"
    widgets: List[DashboardWidget] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_default: bool = True