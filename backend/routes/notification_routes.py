from flask import Blueprint, jsonify, request
from database import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())
    only_unread = request.args.get("unread", "true").lower() == "true"

    db = get_db()
    q = {"userId": user_id}
    if only_unread:
        q["read"] = False
    notifications = list(db.notifications.find(q).sort("createdAt", -1))

    result = []
    for n in notifications:
        result.append({
            "id": n.get("id"),
            "message": n.get("message"),
            "type": n.get("type"),
            "read": n.get("read", False),
            "createdAt": n.get("createdAt"),
        })
    return jsonify(result)


@notifications_bp.route("/read", methods=["POST"])
@jwt_required()
def mark_read():
    user_id = int(get_jwt_identity())
    db = get_db()
    db.notifications.update_many({"userId": user_id}, {"$set": {"read": True}})
    return jsonify({"ok": True})
