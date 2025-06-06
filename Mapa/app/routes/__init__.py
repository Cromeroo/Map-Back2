from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Inicializar la base de datos
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:4173", "https://vite-project-six-ecru.vercel.app"]}},        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    db.init_app(app)

    from ..weather_api import weather_api
    app.register_blueprint(weather_api, url_prefix='/api')

    from .main_routes import main_routes
    app.register_blueprint(main_routes)

    from .auth_routes import auth_routes
    app.register_blueprint(auth_routes, url_prefix='/auth')

    return app