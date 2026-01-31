"""
Servicio de Dashboard y Reportes
Genera estadísticas, métricas y reportes del sistema
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from bson import ObjectId
from app.models.dashboard import (
    TaskStatistics, ProjectStatistics, UserStatistics, ProductivityMetrics,
    DashboardSummary, TaskReport, ProjectReport, UserProductivityReport,
    ReportFilters, TimeRange, MetricType, ChartDataPoint, ChartData
)
from app.models import TaskStatus, Priority
import csv
import json
from io import StringIO

class ReportsService:
    def __init__(self, database):
        self.db = database
    
    def _get_date_range(self, time_range: TimeRange, custom_start: Optional[date] = None, custom_end: Optional[date] = None) -> Tuple[datetime, datetime]:
        """Obtener rango de fechas basado en el tipo de rango"""
        end_date = datetime.utcnow()
        
        if time_range == TimeRange.CUSTOM:
            if custom_start and custom_end:
                return (
                    datetime.combine(custom_start, datetime.min.time()),
                    datetime.combine(custom_end, datetime.max.time())
                )
        
        if time_range == TimeRange.LAST_7_DAYS:
            start_date = end_date - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            start_date = end_date - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            start_date = end_date - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # default
        
        return start_date, end_date
    
    async def get_task_statistics(self, time_range: TimeRange = TimeRange.LAST_30_DAYS, project_id: Optional[str] = None) -> TaskStatistics:
        """Generar estadísticas de tareas"""
        start_date, end_date = self._get_date_range(time_range)
        
        # Filtros base
        base_filter = {}
        if project_id:
            base_filter["project_id"] = ObjectId(project_id)
        
        # Pipeline de agregación para estadísticas generales
        pipeline = [
            {"$match": base_filter},
            {
                "$group": {
                    "_id": None,
                    "total_tasks": {"$sum": 1},
                    "completed_tasks": {"$sum": {"$cond": [{"$eq": ["$status", TaskStatus.COMPLETED]}, 1, 0]}},
                    "pending_tasks": {"$sum": {"$cond": [{"$eq": ["$status", TaskStatus.PENDING]}, 1, 0]}},
                    "in_progress_tasks": {"$sum": {"$cond": [{"$eq": ["$status", TaskStatus.IN_PROGRESS]}, 1, 0]}},
                    "high_priority_tasks": {"$sum": {"$cond": [{"$eq": ["$priority", Priority.HIGH]}, 1, 0]}},
                    "medium_priority_tasks": {"$sum": {"$cond": [{"$eq": ["$priority", Priority.MEDIUM]}, 1, 0]}},
                    "low_priority_tasks": {"$sum": {"$cond": [{"$eq": ["$priority", Priority.LOW]}, 1, 0]}},
                    "overdue_tasks": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$ne": ["$status", TaskStatus.COMPLETED]},
                                        {"$lt": ["$due_date", datetime.utcnow()]}
                                    ]
                                },
                                1, 0
                            ]
                        }
                    }
                }
            }
        ]
        
        result = await self.db.tasks.aggregate(pipeline).to_list(length=1)
        stats = result[0] if result else {}
        
        # Calcular tasa de completación
        total = stats.get("total_tasks", 0)
        completed = stats.get("completed_tasks", 0)
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        # Estadísticas por tiempo
        week_start = datetime.utcnow() - timedelta(days=7)
        month_start = datetime.utcnow() - timedelta(days=30)
        
        tasks_created_this_week = await self.db.tasks.count_documents({
            **base_filter,
            "created_at": {"$gte": week_start}
        })
        
        tasks_completed_this_week = await self.db.tasks.count_documents({
            **base_filter,
            "status": TaskStatus.COMPLETED,
            "updated_at": {"$gte": week_start}
        })
        
        tasks_created_this_month = await self.db.tasks.count_documents({
            **base_filter,
            "created_at": {"$gte": month_start}
        })
        
        tasks_completed_this_month = await self.db.tasks.count_documents({
            **base_filter,
            "status": TaskStatus.COMPLETED,
            "updated_at": {"$gte": month_start}
        })
        
        # Tiempo promedio de completación
        avg_completion_pipeline = [
            {
                "$match": {
                    **base_filter,
                    "status": TaskStatus.COMPLETED,
                    "updated_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$addFields": {
                    "completion_days": {
                        "$divide": [
                            {"$subtract": ["$updated_at", "$created_at"]},
                            86400000  # milisegundos en un día
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_completion_time": {"$avg": "$completion_days"}
                }
            }
        ]
        
        avg_result = await self.db.tasks.aggregate(avg_completion_pipeline).to_list(length=1)
        avg_completion_time = avg_result[0]["avg_completion_time"] if avg_result else None
        
        return TaskStatistics(
            total_tasks=stats.get("total_tasks", 0),
            completed_tasks=completed,
            pending_tasks=stats.get("pending_tasks", 0),
            in_progress_tasks=stats.get("in_progress_tasks", 0),
            overdue_tasks=stats.get("overdue_tasks", 0),
            completion_rate=round(completion_rate, 2),
            average_completion_time=round(avg_completion_time, 2) if avg_completion_time else None,
            high_priority_tasks=stats.get("high_priority_tasks", 0),
            medium_priority_tasks=stats.get("medium_priority_tasks", 0),
            low_priority_tasks=stats.get("low_priority_tasks", 0),
            tasks_created_this_week=tasks_created_this_week,
            tasks_completed_this_week=tasks_completed_this_week,
            tasks_created_this_month=tasks_created_this_month,
            tasks_completed_this_month=tasks_completed_this_month
        )
    
    async def get_project_statistics(self, time_range: TimeRange = TimeRange.LAST_30_DAYS) -> ProjectStatistics:
        """Generar estadísticas de proyectos"""
        start_date, end_date = self._get_date_range(time_range)
        
        # Estadísticas básicas de proyectos
        total_projects = await self.db.projects.count_documents({})
        active_projects = await self.db.projects.count_documents({"status": "active"})
        completed_projects = await self.db.projects.count_documents({"status": "completed"})
        
        # Proyectos vencidos
        overdue_projects = await self.db.projects.count_documents({
            "end_date": {"$lt": datetime.utcnow()},
            "status": {"$ne": "completed"}
        })
        
        # Proyecto más activo (con más tareas)
        most_active_pipeline = [
            {
                "$lookup": {
                    "from": "tasks",
                    "localField": "_id",
                    "foreignField": "project_id",
                    "as": "tasks"
                }
            },
            {
                "$addFields": {
                    "task_count": {"$size": "$tasks"}
                }
            },
            {
                "$sort": {"task_count": -1}
            },
            {
                "$limit": 1
            }
        ]
        
        most_active_result = await self.db.projects.aggregate(most_active_pipeline).to_list(length=1)
        most_active_project = None
        most_active_project_tasks = 0
        
        if most_active_result:
            most_active_project = most_active_result[0]["name"]
            most_active_project_tasks = most_active_result[0]["task_count"]
        
        # Promedio de tareas por proyecto
        avg_tasks_pipeline = [
            {
                "$lookup": {
                    "from": "tasks",
                    "localField": "_id",
                    "foreignField": "project_id",
                    "as": "tasks"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_tasks": {"$avg": {"$size": "$tasks"}}
                }
            }
        ]
        
        avg_tasks_result = await self.db.projects.aggregate(avg_tasks_pipeline).to_list(length=1)
        avg_tasks = avg_tasks_result[0]["avg_tasks"] if avg_tasks_result else 0.0
        
        return ProjectStatistics(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            overdue_projects=overdue_projects,
            average_tasks_per_project=round(avg_tasks, 2),
            most_active_project=most_active_project,
            most_active_project_tasks=most_active_project_tasks
        )
    
    async def get_user_statistics(self, time_range: TimeRange = TimeRange.LAST_30_DAYS) -> UserStatistics:
        """Generar estadísticas de usuarios"""
        start_date, end_date = self._get_date_range(time_range)
        
        total_users = await self.db.users.count_documents({})
        
        # Usuarios activos (con actividad reciente)
        active_users = await self.db.users.count_documents({
            "$or": [
                {"last_login": {"$gte": start_date}},
                {"updated_at": {"$gte": start_date}}
            ]
        })
        
        # Usuario más productivo (más tareas completadas)
        most_productive_pipeline = [
            {
                "$lookup": {
                    "from": "tasks",
                    "localField": "_id",
                    "foreignField": "assigned_to",
                    "as": "assigned_tasks"
                }
            },
            {
                "$addFields": {
                    "completed_tasks_count": {
                        "$size": {
                            "$filter": {
                                "input": "$assigned_tasks",
                                "cond": {"$eq": ["$$this.status", TaskStatus.COMPLETED]}
                            }
                        }
                    }
                }
            },
            {
                "$sort": {"completed_tasks_count": -1}
            },
            {
                "$limit": 1
            }
        ]
        
        most_productive_result = await self.db.users.aggregate(most_productive_pipeline).to_list(length=1)
        most_productive_user = None
        most_productive_user_tasks = 0
        
        if most_productive_result:
            most_productive_user = most_productive_result[0]["username"]
            most_productive_user_tasks = most_productive_result[0]["completed_tasks_count"]
        
        # Promedio de tareas por usuario
        avg_tasks_pipeline = [
            {
                "$lookup": {
                    "from": "tasks",
                    "localField": "_id",
                    "foreignField": "assigned_to",
                    "as": "assigned_tasks"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_tasks": {"$avg": {"$size": "$assigned_tasks"}}
                }
            }
        ]
        
        avg_tasks_result = await self.db.users.aggregate(avg_tasks_pipeline).to_list(length=1)
        avg_tasks = avg_tasks_result[0]["avg_tasks"] if avg_tasks_result else 0.0
        
        # Usuarios con tareas vencidas
        users_with_overdue = await self.db.users.count_documents({
            "_id": {
                "$in": await self.db.tasks.distinct("assigned_to", {
                    "status": {"$ne": TaskStatus.COMPLETED},
                    "due_date": {"$lt": datetime.utcnow()}
                })
            }
        })
        
        return UserStatistics(
            total_users=total_users,
            active_users=active_users,
            most_productive_user=most_productive_user,
            most_productive_user_tasks=most_productive_user_tasks,
            average_tasks_per_user=round(avg_tasks, 2),
            users_with_overdue_tasks=users_with_overdue
        )
    
    async def get_productivity_metrics(self, time_range: TimeRange = TimeRange.LAST_30_DAYS) -> ProductivityMetrics:
        """Generar métricas de productividad"""
        now = datetime.utcnow()
        today_start = datetime.combine(now.date(), datetime.min.time())
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Tareas completadas por periodo
        tasks_completed_today = await self.db.tasks.count_documents({
            "status": TaskStatus.COMPLETED,
            "updated_at": {"$gte": today_start}
        })
        
        tasks_completed_this_week = await self.db.tasks.count_documents({
            "status": TaskStatus.COMPLETED,
            "updated_at": {"$gte": week_start}
        })
        
        tasks_completed_this_month = await self.db.tasks.count_documents({
            "status": TaskStatus.COMPLETED,
            "updated_at": {"$gte": month_start}
        })
        
        # Tendencias de los últimos 7 días
        completion_trend = []
        creation_trend = []
        
        for i in range(7):
            day_start = datetime.combine((now - timedelta(days=i)).date(), datetime.min.time())
            day_end = day_start + timedelta(days=1)
            
            completed_day = await self.db.tasks.count_documents({
                "status": TaskStatus.COMPLETED,
                "updated_at": {"$gte": day_start, "$lt": day_end}
            })
            
            created_day = await self.db.tasks.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end}
            })
            
            completion_trend.insert(0, completed_day)
            creation_trend.insert(0, created_day)
        
        # Métricas de tiempo
        time_metrics_pipeline = [
            {
                "$match": {
                    "status": TaskStatus.COMPLETED,
                    "actual_hours": {"$gt": 0}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_duration": {"$avg": "$actual_hours"},
                    "durations": {"$push": "$actual_hours"}
                }
            }
        ]
        
        time_result = await self.db.tasks.aggregate(time_metrics_pipeline).to_list(length=1)
        avg_duration = None
        median_duration = None
        
        if time_result:
            avg_duration = time_result[0]["avg_duration"]
            durations = sorted(time_result[0]["durations"])
            n = len(durations)
            if n > 0:
                median_duration = durations[n//2] if n % 2 == 1 else (durations[n//2-1] + durations[n//2]) / 2
        
        # Tasas de completación a tiempo
        on_time_pipeline = [
            {
                "$match": {
                    "status": TaskStatus.COMPLETED,
                    "due_date": {"$ne": None}
                }
            },
            {
                "$addFields": {
                    "completed_on_time": {"$lte": ["$updated_at", "$due_date"]},
                    "completed_early": {"$lt": ["$updated_at", {"$subtract": ["$due_date", 86400000]}]}  # 1 día antes
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "on_time": {"$sum": {"$cond": ["$completed_on_time", 1, 0]}},
                    "early": {"$sum": {"$cond": ["$completed_early", 1, 0]}},
                    "late": {"$sum": {"$cond": [{"$not": "$completed_on_time"}, 1, 0]}}
                }
            }
        ]
        
        completion_result = await self.db.tasks.aggregate(on_time_pipeline).to_list(length=1)
        on_time_rate = 0.0
        early_rate = 0.0
        late_rate = 0.0
        
        if completion_result:
            total = completion_result[0]["total"]
            if total > 0:
                on_time_rate = (completion_result[0]["on_time"] / total) * 100
                early_rate = (completion_result[0]["early"] / total) * 100
                late_rate = (completion_result[0]["late"] / total) * 100
        
        return ProductivityMetrics(
            tasks_completed_today=tasks_completed_today,
            tasks_completed_this_week=tasks_completed_this_week,
            tasks_completed_this_month=tasks_completed_this_month,
            completion_trend_7_days=completion_trend,
            creation_trend_7_days=creation_trend,
            average_task_duration=round(avg_duration, 2) if avg_duration else None,
            median_task_duration=round(median_duration, 2) if median_duration else None,
            on_time_completion_rate=round(on_time_rate, 2),
            early_completion_rate=round(early_rate, 2),
            late_completion_rate=round(late_rate, 2)
        )
    
    async def get_dashboard_summary(self, time_range: TimeRange = TimeRange.LAST_30_DAYS, user_id: Optional[str] = None) -> DashboardSummary:
        """Generar resumen completo del dashboard"""
        
        # Obtener todas las estadísticas
        task_stats = await self.get_task_statistics(time_range)
        project_stats = await self.get_project_statistics(time_range)
        user_stats = await self.get_user_statistics(time_range)
        productivity_metrics = await self.get_productivity_metrics(time_range)
        
        # Generar alertas y recomendaciones
        alerts = []
        recommendations = []
        
        if task_stats.overdue_tasks > 0:
            alerts.append(f"Hay {task_stats.overdue_tasks} tareas vencidas que requieren atención")
        
        if project_stats.overdue_projects > 0:
            alerts.append(f"Hay {project_stats.overdue_projects} proyectos vencidos")
        
        if task_stats.completion_rate < 70:
            recommendations.append("La tasa de completación está por debajo del 70%. Considera revisar la carga de trabajo")
        
        if productivity_metrics.late_completion_rate > 30:
            recommendations.append("Más del 30% de las tareas se completan tarde. Revisa los plazos asignados")
        
        return DashboardSummary(
            task_stats=task_stats,
            project_stats=project_stats,
            user_stats=user_stats,
            productivity_metrics=productivity_metrics,
            time_range=time_range,
            alerts=alerts,
            recommendations=recommendations
        )
    
    async def generate_tasks_report(self, filters: Optional[ReportFilters] = None) -> List[TaskReport]:
        """Generar reporte detallado de tareas"""
        query = {}
        
        if filters:
            if filters.start_date:
                query["created_at"] = {"$gte": datetime.combine(filters.start_date, datetime.min.time())}
            if filters.end_date:
                if "created_at" in query:
                    query["created_at"]["$lte"] = datetime.combine(filters.end_date, datetime.max.time())
                else:
                    query["created_at"] = {"$lte": datetime.combine(filters.end_date, datetime.max.time())}
            
            if filters.project_ids:
                query["project_id"] = {"$in": [ObjectId(pid) for pid in filters.project_ids]}
            
            if filters.user_ids:
                query["assigned_to"] = {"$in": [ObjectId(uid) for uid in filters.user_ids]}
            
            if filters.task_statuses:
                query["status"] = {"$in": filters.task_statuses}
            
            if filters.task_priorities:
                query["priority"] = {"$in": filters.task_priorities}
            
            if not filters.include_completed:
                query["status"] = {"$ne": TaskStatus.COMPLETED}
            
            if filters.include_overdue_only:
                query["$and"] = [
                    {"status": {"$ne": TaskStatus.COMPLETED}},
                    {"due_date": {"$lt": datetime.utcnow()}}
                ]
        
        # Pipeline para obtener datos completos
        pipeline = [
            {"$match": query},
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "project_id",
                    "foreignField": "_id",
                    "as": "project"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "assigned_to",
                    "foreignField": "_id",
                    "as": "assigned_user"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "created_by",
                    "foreignField": "_id",
                    "as": "creator"
                }
            },
            {
                "$lookup": {
                    "from": "comments",
                    "localField": "_id",
                    "foreignField": "task_id",
                    "as": "comments"
                }
            },
            {
                "$addFields": {
                    "project_name": {"$arrayElemAt": ["$project.name", 0]},
                    "assigned_username": {"$arrayElemAt": ["$assigned_user.username", 0]},
                    "created_username": {"$arrayElemAt": ["$creator.username", 0]},
                    "comments_count": {"$size": "$comments"},
                    "is_overdue": {
                        "$and": [
                            {"$ne": ["$status", TaskStatus.COMPLETED]},
                            {"$lt": ["$due_date", datetime.utcnow()]}
                        ]
                    },
                    "completion_time_days": {
                        "$cond": [
                            {"$eq": ["$status", TaskStatus.COMPLETED]},
                            {
                                "$divide": [
                                    {"$subtract": ["$updated_at", "$created_at"]},
                                    86400000
                                ]
                            },
                            None
                        ]
                    }
                }
            },
            {"$sort": {"created_at": -1}}
        ]
        
        cursor = self.db.tasks.aggregate(pipeline)
        tasks = await cursor.to_list(length=None)
        
        report = []
        for task in tasks:
            report.append(TaskReport(
                id=str(task["_id"]),
                title=task["title"],
                description=task.get("description"),
                status=task["status"],
                priority=task["priority"],
                project_name=task.get("project_name"),
                assigned_username=task.get("assigned_username"),
                created_username=task.get("created_username"),
                created_at=task["created_at"],
                updated_at=task["updated_at"],
                due_date=task["due_date"].date() if task.get("due_date") else None,
                estimated_hours=task.get("estimated_hours", 0.0),
                actual_hours=task.get("actual_hours", 0.0),
                completion_time_days=round(task["completion_time_days"], 2) if task.get("completion_time_days") else None,
                is_overdue=bool(task.get("is_overdue", False)),
                comments_count=task.get("comments_count", 0)
            ))
        
        return report
    
    def export_to_csv(self, data: List[Dict], filename: str = "report.csv") -> str:
        """Exportar datos a formato CSV"""
        if not data:
            return ""
        
        output = StringIO()
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Convertir datetime a string para CSV
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        processed_row[key] = value.isoformat()
                    elif isinstance(value, date):
                        processed_row[key] = value.isoformat()
                    else:
                        processed_row[key] = value
                writer.writerow(processed_row)
        
        return output.getvalue()
    
    def export_to_json(self, data: List[Dict], filename: str = "report.json") -> str:
        """Exportar datos a formato JSON"""
        # Convertir datetime y date a string para JSON
        def json_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(data, default=json_serializer, indent=2, ensure_ascii=False)