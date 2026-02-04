from flask import Blueprint, request, jsonify
from database import get_db, get_next_id
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

tasks_bp = Blueprint("tasks", __name__)


def _task_to_json(t):
    if not t:
        return None
    t = dict(t)
    t.pop("_id", None)
    return t


def _get_user_id():
    return int(get_jwt_identity())


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def list_tasks():
    db = get_db()
    tasks = list(db.tasks.find({}))
    projects = {p["id"]: p for p in db.projects.find({})}
    users = {u["id"]: u for u in db.users.find({}, {"username": 1, "id": 1})}

    result = []
    for t in tasks:
        t = _task_to_json(t)
        t["projectName"] = projects.get(t.get("projectId"), {}).get("name", "Sin proyecto")
        t["assignedToName"] = users.get(t.get("assignedTo"), {}).get("username", "Sin asignar") if t.get("assignedTo") else "Sin asignar"
        result.append(t)
    return jsonify(result)


@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    user_id = _get_user_id()
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "El título es requerido"}), 400

    db = get_db()
    task_id = get_next_id("tasks")
    now = datetime.utcnow().isoformat() + "Z"
    task = {
        "id": task_id,
        "title": title,
        "description": (data.get("description") or "").strip(),
        "status": data.get("status") or "Pendiente",
        "priority": data.get("priority") or "Media",
        "projectId": int(data.get("projectId") or 0) or None,
        "assignedTo": int(data.get("assignedTo") or 0) or None,
        "dueDate": (data.get("dueDate") or "").strip() or None,
        "estimatedHours": float(data.get("estimatedHours") or 0) or None,
        "actualHours": 0,
        "createdBy": user_id,
        "createdAt": now,
        "updatedAt": now,
    }
    db.tasks.insert_one(task)

    db.history.insert_one({
        "id": get_next_id("history"),
        "taskId": task_id,
        "userId": user_id,
        "action": "CREATED",
        "oldValue": "",
        "newValue": title,
        "timestamp": now,
    })

    if task.get("assignedTo"):
        db.notifications.insert_one({
            "id": get_next_id("notifications"),
            "userId": task["assignedTo"],
            "message": f"Nueva tarea asignada: {title}",
            "type": "task_assigned",
            "read": False,
            "createdAt": now,
        })

    return jsonify(_task_to_json(task)), 201


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    db = get_db()
    task = db.tasks.find_one({"id": task_id})
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(_task_to_json(task))


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = _get_user_id()
    data = request.get_json() or {}
    db = get_db()
    old = db.tasks.find_one({"id": task_id})
    if not old:
        return jsonify({"error": "Tarea no encontrada"}), 404

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "El título es requerido"}), 400

    now = datetime.utcnow().isoformat() + "Z"
    task = {
        "id": task_id,
        "title": title,
        "description": (data.get("description") or "").strip(),
        "status": data.get("status") or "Pendiente",
        "priority": data.get("priority") or "Media",
        "projectId": int(data.get("projectId") or 0) or None,
        "assignedTo": int(data.get("assignedTo") or 0) or None,
        "dueDate": (data.get("dueDate") or "").strip() or None,
        "estimatedHours": float(data.get("estimatedHours") or 0) or None,
        "actualHours": old.get("actualHours") or 0,
        "createdBy": old["createdBy"],
        "createdAt": old["createdAt"],
        "updatedAt": now,
    }

    if old.get("status") != task["status"]:
        db.history.insert_one({
            "id": get_next_id("history"),
            "taskId": task_id,
            "userId": user_id,
            "action": "STATUS_CHANGED",
            "oldValue": old.get("status", ""),
            "newValue": task["status"],
            "timestamp": now,
        })
    if old.get("title") != task["title"]:
        db.history.insert_one({
            "id": get_next_id("history"),
            "taskId": task_id,
            "userId": user_id,
            "action": "TITLE_CHANGED",
            "oldValue": old.get("title", ""),
            "newValue": task["title"],
            "timestamp": now,
        })

    db.tasks.update_one({"id": task_id}, {"$set": task})

    if task.get("assignedTo"):
        db.notifications.insert_one({
            "id": get_next_id("notifications"),
            "userId": task["assignedTo"],
            "message": f"Tarea actualizada: {title}",
            "type": "task_updated",
            "read": False,
            "createdAt": now,
        })

    return jsonify(_task_to_json(task))


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = _get_user_id()
    db = get_db()
    task = db.tasks.find_one({"id": task_id})
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404

    now = datetime.utcnow().isoformat() + "Z"
    db.history.insert_one({
        "id": get_next_id("history"),
        "taskId": task_id,
        "userId": user_id,
        "action": "DELETED",
        "oldValue": task.get("title", ""),
        "newValue": "",
        "timestamp": now,
    })
    db.tasks.delete_one({"id": task_id})
    return jsonify({"ok": True})


@tasks_bp.route("/stats", methods=["GET"])
@jwt_required()
def task_stats():
    db = get_db()
    tasks = list(db.tasks.find({}))
    from datetime import datetime
    now = datetime.utcnow()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "Completada")
    pending = total - completed
    high_priority = sum(1 for t in tasks if t.get("priority") in ("Alta", "Crítica"))
    overdue = 0
    for t in tasks:
        if t.get("status") == "Completada":
            continue
        due = t.get("dueDate")
        if due:
            try:
                due_d = datetime.fromisoformat(due.replace("Z", "+00:00"))
                if due_d.replace(tzinfo=None) < now:
                    overdue += 1
            except Exception:
                pass
    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending,
        "highPriority": high_priority,
        "overdue": overdue,
    })


@tasks_bp.route("/search", methods=["POST"])
@jwt_required()
def search_tasks():
    data = request.get_json() or {}
    search_text = (data.get("text") or "").strip()
    status = (data.get("status") or "").strip()
    priority = (data.get("priority") or "").strip()
    project_id = data.get("projectId")

    db = get_db()
    q = {}
    if search_text:
        q["$or"] = [
            {"title": {"$regex": search_text, "$options": "i"}},
            {"description": {"$regex": search_text, "$options": "i"}},
        ]
    if status:
        q["status"] = status
    if priority:
        q["priority"] = priority
    if project_id:
        q["projectId"] = int(project_id)

    tasks = list(db.tasks.find(q))
    projects = {p["id"]: p for p in db.projects.find({})}
    result = []
    for t in tasks:
        t = _task_to_json(t)
        t["projectName"] = projects.get(t.get("projectId"), {}).get("name", "Sin proyecto")
        result.append(t)
    return jsonify(result)
