from flask import Blueprint, request, jsonify
from database import get_db, get_next_id
from flask_jwt_extended import jwt_required

projects_bp = Blueprint("projects", __name__)


def _project_to_json(p):
    if not p:
        return None
    p = dict(p)
    p.pop("_id", None)
    return p


@projects_bp.route("", methods=["GET"])
@jwt_required()
def list_projects():
    db = get_db()
    projects = list(db.projects.find({}))
    return jsonify([_project_to_json(p) for p in projects])


@projects_bp.route("", methods=["POST"])
@jwt_required()
def create_project():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "El nombre es requerido"}), 400

    db = get_db()
    project_id = get_next_id("projects")
    project = {
        "id": project_id,
        "name": name,
        "description": (data.get("description") or "").strip(),
    }
    db.projects.insert_one(project)
    return jsonify(_project_to_json(project)), 201


@projects_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project(project_id):
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "El nombre es requerido"}), 400

    db = get_db()
    project = db.projects.find_one({"id": project_id})
    if not project:
        return jsonify({"error": "Proyecto no encontrado"}), 404

    project["name"] = name
    project["description"] = (data.get("description") or "").strip()
    db.projects.update_one({"id": project_id}, {"$set": project})
    return jsonify(_project_to_json(project))


@projects_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    db = get_db()
    result = db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Proyecto no encontrado"}), 404
    return jsonify({"ok": True})
