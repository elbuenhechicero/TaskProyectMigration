from flask import Blueprint, request, jsonify
from database import get_db
from utils.security import check_password, hash_password
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

auth_bp = Blueprint("auth", __name__)


def _user_to_json(user):
    return {"id": user["id"], "username": user["username"]}


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    db = get_db()
    user = db.users.find_one({"username": username})
    if not user or not check_password(user["password"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(identity=str(user["id"]))
    return jsonify({"token": token, "user": _user_to_json(user)})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    db = get_db()
    user = db.users.find_one({"id": user_id})
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(_user_to_json(user))


@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    db = get_db()
    users = list(db.users.find({}, {"password": 0}))
    return jsonify([{"id": u["id"], "username": u["username"]} for u in users])
