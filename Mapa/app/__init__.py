from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from sqlalchemy import NullPool

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- CONFIGURACIÓN OPTIMIZADA PARA CONEXIONES DE BASE DE DATOS ---
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,           # Recicla conexiones cada 280 segundos
        'pool_pre_ping': True,         # Verifica la conexión antes de usarla
        'pool_size': 5,                # Máximo 5 conexiones en el pool
        'max_overflow': 0,             # Sin conexiones adicionales
        'poolclass': NullPool,         # Usa NullPool para cerrar conexiones inmediatamente
    }
    # ----------------------------------------------------------------

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

    # --- MANEJO AUTOMÁTICO DE CIERRE DE SESIONES ---
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            db.session.remove()
        except Exception:
            pass
    
    @app.teardown_request
    def teardown_request(exception=None):
        try:
            db.session.close()
        except Exception:
            pass
    # -----------------------------------------------

    return app