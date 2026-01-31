"""
Router para Dashboard y Reportes
Sistema de estadísticas, métricas y reportes del proyecto
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import PlainTextResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
from app.core.database import get_database
from app.models.dashboard import (
    TaskStatistics, ProjectStatistics, UserStatistics, ProductivityMetrics,
    DashboardSummary, TaskReport, ProjectReport, UserProductivityReport,
    ReportFilters, ReportRequest, ReportResponse, TimeRange, MetricType,
    ReportFormat, ChartData, ChartDataPoint
)
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user
from app.utils.reports_service import ReportsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Reports"])

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Rango de tiempo para las estadísticas"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener resumen completo del dashboard con todas las estadísticas"""
    
    reports_service = ReportsService(db)
    summary = await reports_service.get_dashboard_summary(time_range, str(current_user.id))
    
    return summary

@router.get("/stats/tasks", response_model=TaskStatistics)
async def get_task_statistics(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Rango de tiempo"),
    project_id: Optional[str] = Query(None, description="Filtrar por proyecto específico"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas detalladas de tareas"""
    
    reports_service = ReportsService(db)
    stats = await reports_service.get_task_statistics(time_range, project_id)
    
    return stats

@router.get("/stats/projects", response_model=ProjectStatistics)
async def get_project_statistics(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Rango de tiempo"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas detalladas de proyectos"""
    
    reports_service = ReportsService(db)
    stats = await reports_service.get_project_statistics(time_range)
    
    return stats

@router.get("/stats/users", response_model=UserStatistics)
async def get_user_statistics(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Rango de tiempo"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas detalladas de usuarios"""
    
    # Solo admin puede ver estadísticas de usuarios
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view user statistics"
        )
    
    reports_service = ReportsService(db)
    stats = await reports_service.get_user_statistics(time_range)
    
    return stats

@router.get("/stats/productivity", response_model=ProductivityMetrics)
async def get_productivity_metrics(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Rango de tiempo"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener métricas de productividad"""
    
    reports_service = ReportsService(db)
    metrics = await reports_service.get_productivity_metrics(time_range)
    
    return metrics

@router.get("/charts/task-completion-trend", response_model=ChartData)
async def get_task_completion_trend(
    days: int = Query(7, ge=1, le=90, description="Número de días hacia atrás"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener datos para gráfico de tendencia de completación de tareas"""
    
    reports_service = ReportsService(db)
    metrics = await reports_service.get_productivity_metrics()
    
    # Crear datos para el gráfico
    data_points = []
    for i, completions in enumerate(metrics.completion_trend_7_days):
        day_date = (datetime.utcnow() - timedelta(days=6-i)).date()
        data_points.append(ChartDataPoint(
            label=day_date.strftime("%d/%m"),
            value=float(completions),
            date=day_date
        ))
    
    return ChartData(
        chart_type="line",
        title="Tendencia de Completación de Tareas",
        x_axis_label="Fecha",
        y_axis_label="Tareas Completadas",
        data_points=data_points,
        colors=["#4CAF50"]
    )

@router.get("/charts/task-status-distribution", response_model=ChartData)
async def get_task_status_distribution(
    project_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener datos para gráfico de distribución de estados de tareas"""
    
    reports_service = ReportsService(db)
    stats = await reports_service.get_task_statistics(project_id=project_id)
    
    data_points = [
        ChartDataPoint(label="Pendientes", value=float(stats.pending_tasks)),
        ChartDataPoint(label="En Progreso", value=float(stats.in_progress_tasks)),
        ChartDataPoint(label="Completadas", value=float(stats.completed_tasks)),
        ChartDataPoint(label="Vencidas", value=float(stats.overdue_tasks))
    ]
    
    return ChartData(
        chart_type="pie",
        title="Distribución de Estados de Tareas",
        data_points=data_points,
        colors=["#FFC107", "#2196F3", "#4CAF50", "#F44336"]
    )

@router.get("/charts/priority-distribution", response_model=ChartData)
async def get_priority_distribution(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener datos para gráfico de distribución de prioridades"""
    
    reports_service = ReportsService(db)
    stats = await reports_service.get_task_statistics()
    
    data_points = [
        ChartDataPoint(label="Alta", value=float(stats.high_priority_tasks)),
        ChartDataPoint(label="Media", value=float(stats.medium_priority_tasks)),
        ChartDataPoint(label="Baja", value=float(stats.low_priority_tasks))
    ]
    
    return ChartData(
        chart_type="doughnut",
        title="Distribución de Prioridades",
        data_points=data_points,
        colors=["#F44336", "#FF9800", "#4CAF50"]
    )

@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Generar reporte personalizado"""
    
    start_time = datetime.utcnow()
    reports_service = ReportsService(db)
    
    # Generar ID único para el reporte
    report_id = str(uuid.uuid4())
    
    try:
        if report_request.report_type == MetricType.TASKS:
            # Reporte de tareas
            data = await reports_service.generate_tasks_report(report_request.filters)
            
            # Convertir a diccionarios para la respuesta
            data_dicts = [task.dict() for task in data]
            
            # Resumen
            summary = {
                "total_tasks": len(data),
                "completed_tasks": sum(1 for task in data if task.status == "completed"),
                "overdue_tasks": sum(1 for task in data if task.is_overdue),
                "average_completion_time": sum(
                    task.completion_time_days for task in data 
                    if task.completion_time_days is not None
                ) / len([task for task in data if task.completion_time_days is not None]) if any(
                    task.completion_time_days for task in data
                ) else 0
            }
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report type {report_request.report_type} not implemented yet"
            )
        
        # Calcular tiempo de ejecución
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Crear respuesta
        response = ReportResponse(
            report_id=report_id,
            report_type=report_request.report_type,
            format=report_request.format,
            filters_applied=report_request.filters,
            summary=summary,
            data=data_dicts,
            total_records=len(data_dicts),
            execution_time_ms=execution_time
        )
        
        # Si se requiere exportación, procesar en background
        if report_request.format in [ReportFormat.CSV, ReportFormat.PDF]:
            # Aquí se podría implementar exportación a archivos
            # background_tasks.add_task(export_report_to_file, report_id, data_dicts, report_request.format)
            pass
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

@router.get("/reports/tasks/export")
async def export_tasks_report(
    format: ReportFormat = Query(ReportFormat.CSV, description="Formato de exportación"),
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin"),
    project_ids: Optional[str] = Query(None, description="IDs de proyectos separados por comas"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Exportar reporte de tareas en formato CSV o JSON"""
    
    reports_service = ReportsService(db)
    
    # Construir filtros
    filters = ReportFilters()
    if start_date:
        filters.start_date = start_date
    if end_date:
        filters.end_date = end_date
    if project_ids:
        filters.project_ids = [pid.strip() for pid in project_ids.split(",")]
    
    # Generar datos del reporte
    tasks = await reports_service.generate_tasks_report(filters)
    data_dicts = [task.dict() for task in tasks]
    
    if format == ReportFormat.CSV:
        csv_content = reports_service.export_to_csv(data_dicts, "tasks_report.csv")
        
        return PlainTextResponse(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=tasks_report.csv"}
        )
    
    elif format == ReportFormat.JSON:
        json_content = reports_service.export_to_json(data_dicts, "tasks_report.json")
        
        return PlainTextResponse(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=tasks_report.json"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no soportado. Use CSV o JSON."
        )

@router.get("/reports/productivity/{user_id}", response_model=UserProductivityReport)
async def get_user_productivity_report(
    user_id: str,
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Rango de tiempo"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener reporte de productividad de un usuario específico"""
    
    # Solo admin o el propio usuario puede ver su reporte de productividad
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's productivity report"
        )
    
    # Verificar que el usuario existe
    from bson import ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generar reporte de productividad
    start_date, end_date = ReportsService(db)._get_date_range(time_range)
    
    # Estadísticas de tareas del usuario
    user_tasks = await db.tasks.find({"assigned_to": ObjectId(user_id)}).to_list(length=None)
    
    assigned_tasks = len(user_tasks)
    completed_tasks = sum(1 for task in user_tasks if task["status"] == "completed")
    pending_tasks = sum(1 for task in user_tasks if task["status"] == "todo")
    overdue_tasks = sum(1 for task in user_tasks 
                       if task["status"] != "completed" and 
                       task.get("due_date") and 
                       task["due_date"] < datetime.utcnow())
    
    completion_rate = (completed_tasks / assigned_tasks * 100) if assigned_tasks > 0 else 0.0
    
    # Tiempo promedio de completación
    completed_task_times = []
    total_estimated = 0.0
    total_actual = 0.0
    
    for task in user_tasks:
        if task["status"] == "completed":
            completion_time = (task["updated_at"] - task["created_at"]).days
            completed_task_times.append(completion_time)
        
        total_estimated += task.get("estimated_hours", 0.0)
        total_actual += task.get("actual_hours", 0.0)
    
    avg_completion_time = sum(completed_task_times) / len(completed_task_times) if completed_task_times else None
    time_accuracy = (1 - abs(total_actual - total_estimated) / total_estimated * 100) if total_estimated > 0 else 0.0
    
    # Actividad del mes
    month_start = datetime.utcnow() - timedelta(days=30)
    
    tasks_created_this_month = await db.tasks.count_documents({
        "created_by": ObjectId(user_id),
        "created_at": {"$gte": month_start}
    })
    
    tasks_completed_this_month = await db.tasks.count_documents({
        "assigned_to": ObjectId(user_id),
        "status": "completed",
        "updated_at": {"$gte": month_start}
    })
    
    comments_this_month = await db.comments.count_documents({
        "author_id": ObjectId(user_id),
        "created_at": {"$gte": month_start}
    })
    
    # Proyectos activos
    active_projects = await db.projects.find({
        "_id": {"$in": [task["project_id"] for task in user_tasks if task.get("project_id")]}
    }).distinct("name")
    
    return UserProductivityReport(
        user_id=user_id,
        username=user["username"],
        email=user["email"],
        assigned_tasks=assigned_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=round(completion_rate, 2),
        average_completion_time=round(avg_completion_time, 2) if avg_completion_time else None,
        total_estimated_hours=total_estimated,
        total_actual_hours=total_actual,
        time_accuracy=round(time_accuracy, 2),
        tasks_created_this_month=tasks_created_this_month,
        tasks_completed_this_month=tasks_completed_this_month,
        comments_this_month=comments_this_month,
        active_projects=active_projects
    )

# Endpoints adicionales para widgets específicos del dashboard
@router.get("/widgets/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Límite de actividades"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener actividad reciente para widget del dashboard"""
    
    # Obtener actividad reciente del historial
    recent_history = await db.history.find({}).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    activities = []
    for record in recent_history:
        # Obtener información del usuario
        user = await db.users.find_one({"_id": record["user_id"]})
        username = user["username"] if user else "Unknown"
        
        activities.append({
            "id": str(record["_id"]),
            "action": record["action"],
            "description": record["description"],
            "username": username,
            "timestamp": record["timestamp"],
            "entity_type": record.get("entity_type"),
            "entity_id": str(record.get("entity_id", ""))
        })
    
    return {"activities": activities}

@router.get("/widgets/overdue-tasks")
async def get_overdue_tasks_widget(
    limit: int = Query(5, ge=1, le=20, description="Límite de tareas vencidas"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener tareas vencidas para widget del dashboard"""
    
    # Filtro base: solo tareas no completadas y vencidas
    filter_query = {
        "status": {"$ne": "completed"},
        "due_date": {"$lt": datetime.utcnow()}
    }
    
    # Si no es admin, solo ver sus tareas asignadas
    if not current_user.is_admin:
        filter_query["assigned_to"] = current_user.id
    
    overdue_tasks = await db.tasks.find(filter_query).sort("due_date", 1).limit(limit).to_list(length=limit)
    
    tasks = []
    for task in overdue_tasks:
        # Obtener información adicional
        project = None
        if task.get("project_id"):
            project = await db.projects.find_one({"_id": task["project_id"]})
        
        assigned_user = None
        if task.get("assigned_to"):
            assigned_user = await db.users.find_one({"_id": task["assigned_to"]})
        
        days_overdue = (datetime.utcnow() - task["due_date"]).days
        
        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "priority": task["priority"],
            "due_date": task["due_date"].date().isoformat(),
            "days_overdue": days_overdue,
            "project_name": project["name"] if project else None,
            "assigned_username": assigned_user["username"] if assigned_user else None
        })
    
    return {
        "overdue_tasks": tasks,
        "total_overdue": len(tasks)
    }