from flask import Blueprint, request, jsonify
from database import get_db
from flask_jwt_extended import jwt_required
from io import StringIO
import csv

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/<report_type>", methods=["GET"])
@jwt_required()
def get_report(report_type):
    db = get_db()
    text = f"=== REPORTE: {report_type.upper()} ===\n\n"

    if report_type == "tasks":
        tasks = list(db.tasks.find({}))
        status_count = {}
        for t in tasks:
            s = t.get("status") or "Pendiente"
            status_count[s] = status_count.get(s, 0) + 1
        for status, count in status_count.items():
            text += f"{status}: {count} tareas\n"
    elif report_type == "projects":
        projects = list(db.projects.find({}))
        for p in projects:
            count = db.tasks.count_documents({"projectId": p["id"]})
            text += f"{p['name']}: {count} tareas\n"
    elif report_type == "users":
        users = list(db.users.find({}, {"username": 1, "id": 1}))
        for u in users:
            count = db.tasks.count_documents({"assignedTo": u["id"]})
            text += f"{u['username']}: {count} tareas asignadas\n"
    else:
        return jsonify({"error": "Tipo de reporte no válido"}), 400

    return jsonify({"report": text})


@reports_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_csv():
    db = get_db()
    tasks = list(db.tasks.find({}))
    projects = {p["id"]: p for p in db.projects.find({})}

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Título", "Estado", "Prioridad", "Proyecto"])
    for t in tasks:
        pname = projects.get(t.get("projectId"), {}).get("name", "Sin proyecto") if t.get("projectId") else "Sin proyecto"
        writer.writerow([
            t.get("id"),
            t.get("title", ""),
            t.get("status", "Pendiente"),
            t.get("priority", "Media"),
            pname,
        ])

    return output.getvalue(), 200, {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=export_tasks.csv",
    }
