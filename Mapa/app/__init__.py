from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
        app,
        origins=["http://localhost:5173", "http://localhost:4173"],        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    app.config.from_object(Config)
    
    db.init_app(app)
    
    JWTManager(app)

    # Registrar Blueprints
    from .routes.main_routes import main_routes
    app.register_blueprint(main_routes)

    from .routes.auth_routes import auth_routes
    app.register_blueprint(auth_routes, url_prefix="/auth")


    # 🔥 Devuelve la app dentro del contexto correcto
    with app.app_context():
        db.create_all()  # Si aún no hay tablas, las crea
        print("✅ Base de datos inicializada correctamente")

    return app
