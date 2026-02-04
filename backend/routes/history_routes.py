from flask import Blueprint, request, jsonify
from database import get_db
from flask_jwt_extended import jwt_required

history_bp = Blueprint("history", __name__)


def _entry_to_json(e):
    if not e:
        return None
    e = dict(e)
    e.pop("_id", None)
    return e


@history_bp.route("", methods=["GET"])
@jwt_required()
def list_history():
    task_id = request.args.get("taskId", type=int)
    db = get_db()
    users = {u["id"]: u for u in db.users.find({}, {"username": 1, "id": 1})}

    if task_id:
        entries = list(db.history.find({"taskId": task_id}).sort("timestamp", 1))
    else:
        entries = list(db.history.find({}).sort("timestamp", -1).limit(100))

    result = []
    for e in entries:
        e = _entry_to_json(e)
        e["username"] = users.get(e.get("userId"), {}).get("username", "Desconocido")
        result.append(e)
    return jsonify(result)
