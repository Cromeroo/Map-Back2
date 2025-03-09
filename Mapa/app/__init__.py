from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🔥 Asegurarse de inicializar la base de datos correctamente
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
