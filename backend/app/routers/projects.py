"""
Router para gestión de proyectos (CRUD completo)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.core.database import get_database
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectInDB, ProjectWithStats
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0, description="Número de proyectos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de proyectos a devolver"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Listar proyectos con paginación y filtros"""
    
    # Construir filtros
    filter_query = {}
    
    if search:
        filter_query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Obtener proyectos
    cursor = db.projects.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
    projects = await cursor.to_list(length=limit)
    
    # Convertir a response models
    projects_response = []
    for project_doc in projects:
        # Contar tareas del proyecto
        task_count = await db.tasks.count_documents({"project_id": project_doc["_id"]})
        
        projects_response.append(ProjectResponse(
            id=str(project_doc["_id"]),
            name=project_doc["name"],
            description=project_doc.get("description"),
            created_by=str(project_doc["created_by"]),
            task_count=task_count,
            created_at=project_doc["created_at"],
            updated_at=project_doc["updated_at"]
        ))
    
    return projects_response

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Crear nuevo proyecto"""
    
    # Verificar que no existe un proyecto con el mismo nombre
    existing_project = await db.projects.find_one({"name": project.name})
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )
    
    # Crear proyecto
    project_doc = {
        "name": project.name,
        "description": project.description,
        "created_by": current_user.id,
        "task_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.projects.insert_one(project_doc)
    project_doc["_id"] = result.inserted_id
    
    return ProjectResponse(
        id=str(result.inserted_id),
        name=project.name,
        description=project.description,
        created_by=str(current_user.id),
        task_count=0,
        created_at=project_doc["created_at"],
        updated_at=project_doc["updated_at"]
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener un proyecto por ID"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project_doc = await db.projects.find_one({"_id": ObjectId(project_id)})
    
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Contar tareas del proyecto
    task_count = await db.tasks.count_documents({"project_id": ObjectId(project_id)})
    
    return ProjectResponse(
        id=str(project_doc["_id"]),
        name=project_doc["name"],
        description=project_doc.get("description"),
        created_by=str(project_doc["created_by"]),
        task_count=task_count,
        created_at=project_doc["created_at"],
        updated_at=project_doc["updated_at"]
    )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Actualizar un proyecto"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verificar que el proyecto existe
    existing_project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Solo el creador o admin puede actualizar el proyecto
    if not current_user.is_admin and str(existing_project["created_by"]) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this project"
        )
    
    # Construir update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if project_update.name is not None:
        # Verificar que el nombre no existe en otro proyecto
        existing_name = await db.projects.find_one({
            "name": project_update.name,
            "_id": {"$ne": ObjectId(project_id)}
        })
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name already exists"
            )
        update_data["name"] = project_update.name
    
    if project_update.description is not None:
        update_data["description"] = project_update.description
    
    # Actualizar proyecto
    await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_data}
    )
    
    # Obtener proyecto actualizado
    updated_project = await db.projects.find_one({"_id": ObjectId(project_id)})
    
    # Contar tareas del proyecto
    task_count = await db.tasks.count_documents({"project_id": ObjectId(project_id)})
    
    return ProjectResponse(
        id=str(updated_project["_id"]),
        name=updated_project["name"],
        description=updated_project.get("description"),
        created_by=str(updated_project["created_by"]),
        task_count=task_count,
        created_at=updated_project["created_at"],
        updated_at=updated_project["updated_at"]
    )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Eliminar un proyecto"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verificar que el proyecto existe
    project_doc = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Solo el creador o admin puede eliminar el proyecto
    if not current_user.is_admin and str(project_doc["created_by"]) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this project"
        )
    
    # Verificar si hay tareas asociadas
    task_count = await db.tasks.count_documents({"project_id": ObjectId(project_id)})
    if task_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete project. It has {task_count} associated tasks. Delete tasks first or reassign them."
        )
    
    # Eliminar proyecto
    await db.projects.delete_one({"_id": ObjectId(project_id)})
    
    return {"message": f"Project '{project_doc['name']}' deleted successfully"}

@router.get("/{project_id}/stats", response_model=ProjectWithStats)
async def get_project_stats(
    project_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas detalladas de un proyecto"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verificar que el proyecto existe
    project_doc = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Obtener estadísticas de tareas
    pipeline = [
        {"$match": {"project_id": ObjectId(project_id)}},
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    tasks_by_status = {}
    total_tasks = 0
    completed_tasks = 0
    
    async for result in db.tasks.aggregate(pipeline):
        status = result["_id"]
        count = result["count"]
        tasks_by_status[status] = count
        total_tasks += count
        if status == "Completada":
            completed_tasks = count
    
    # Calcular tasa de completitud
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    return ProjectWithStats(
        id=str(project_doc["_id"]),
        name=project_doc["name"],
        description=project_doc.get("description"),
        created_by=str(project_doc["created_by"]),
        task_count=total_tasks,
        created_at=project_doc["created_at"],
        updated_at=project_doc["updated_at"],
        tasks_by_status=tasks_by_status,
        completion_rate=round(completion_rate, 2)
    )