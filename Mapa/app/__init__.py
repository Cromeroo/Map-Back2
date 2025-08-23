from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- SOLUCIÓN 2 (No sé que hacer :,v) ---
    # Añade estas opciones para que SQLAlchemy maneje mejor las conexiones
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    # ------------------------------------

    CORS(
        app,
        origins=["http://localhost:5173", "http://localhost:4173", "https://vite-project-six-ecru.vercel.app"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    db.init_app(app)
    
    JWTManager(app)

    # Registrar Blueprints
    from .routes.main_routes import main_routes
    app.register_blueprint(main_routes)

    from .routes.auth_routes import auth_routes
    app.register_blueprint(auth_routes, url_prefix="/auth")

    # --- SOLUCIÓN 1 (LA MÁS IMPORTANTE) ---
    # Esta función se ejecutará después de cada petición para cerrar la sesión
    # y devolver la conexión a la base de datos al pool.
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    # -----------------------------------------

    # Crea las tablas de la base de datos si no existen
    #with app.app_context():
    #    db.create_all()
    #    print("✅ Base de datos inicializada correctamente")

    return app