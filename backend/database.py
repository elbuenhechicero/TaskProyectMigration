from pymongo import MongoClient
from config import Config

_client = None
_db = None


def get_db():
    """Obtiene la conexión a la base de datos MongoDB."""
    global _db
    if _db is None:
        global _client
        _client = MongoClient(Config.MONGO_URI)
        _db = _client[Config.MONGO_DB_NAME]
    return _db


def get_next_id(collection_name: str) -> int:
    """Obtiene el siguiente ID numérico para una colección."""
    db = get_db()
    col = db[collection_name]
    doc = col.find_one(filter={"id": {"$exists": True}}, sort=[("id", -1)])
    return (doc["id"] + 1) if doc else 1


def init_db():
    """Inicializa la BD con índices y datos por defecto si no existen."""
    db = get_db()
    # Índices para búsquedas frecuentes
    db.tasks.create_index("projectId")
    db.tasks.create_index("assignedTo")
    db.tasks.create_index("status")
    db.comments.create_index("taskId")
    db.history.create_index("taskId")
    db.notifications.create_index([("userId", 1), ("read", 1)])

    # Datos iniciales solo si no hay usuarios
    if db.users.count_documents({}) == 0:
        from utils.security import hash_password
        db.users.insert_many([
            {"id": 1, "username": "admin", "password": hash_password("admin")},
            {"id": 2, "username": "user1", "password": hash_password("user1")},
            {"id": 3, "username": "user2", "password": hash_password("user2")},
        ])
    return db
