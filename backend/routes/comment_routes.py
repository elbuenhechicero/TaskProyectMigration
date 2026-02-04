from flask import Blueprint, request, jsonify
from database import get_db, get_next_id
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

comments_bp = Blueprint("comments", __name__)


def _comment_to_json(c):
    if not c:
        return None
    c = dict(c)
    c.pop("_id", None)
    return c


@comments_bp.route("", methods=["GET"])
@jwt_required()
def list_comments():
    task_id = request.args.get("taskId", type=int)
    if not task_id:
        return jsonify({"error": "taskId requerido"}), 400

    db = get_db()
    comments = list(db.comments.find({"taskId": task_id}))
    users = {u["id"]: u for u in db.users.find({}, {"username": 1, "id": 1})}
    result = []
    for c in comments:
        c = _comment_to_json(c)
        c["username"] = users.get(c.get("userId"), {}).get("username", "Usuario")
        result.append(c)
    return jsonify(result)


@comments_bp.route("", methods=["POST"])
@jwt_required()
def create_comment():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    task_id = data.get("taskId")
    text = (data.get("commentText") or data.get("text") or "").strip()

    if not task_id:
        return jsonify({"error": "ID de tarea requerido"}), 400
    if not text:
        return jsonify({"error": "El comentario no puede estar vacío"}), 400

    db = get_db()
    comment_id = get_next_id("comments")
    now = datetime.utcnow().isoformat() + "Z"
    comment = {
        "id": comment_id,
        "taskId": int(task_id),
        "userId": user_id,
        "commentText": text,
        "createdAt": now,
    }
    db.comments.insert_one(comment)
    return jsonify(_comment_to_json(comment)), 201
