from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from Mapa.config import Config

# Inicializar la base de datos
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configurar la aplicación
    app.config.from_object(Config)

    # Configurar CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    # Configurar caché
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    # Inicializar base de datos
    db.init_app(app)

    # Importar y registrar Blueprints
    from ..weather_api import weather_api
    app.register_blueprint(weather_api, url_prefix='/api')

    from .main_routes import main_routes
    app.register_blueprint(main_routes)

    return app
