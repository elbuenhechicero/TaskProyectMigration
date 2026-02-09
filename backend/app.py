import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import init_db
from routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 horas

    CORS(app, origins=["*"], supports_credentials=True)
    JWTManager(app)
    register_blueprints(app)

    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == "__main__":
    # Para producción (Render) usa PORT del entorno, para desarrollo usa 5000
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") != "production"
    
    app.run(host="0.0.0.0", port=port, debug=debug)
