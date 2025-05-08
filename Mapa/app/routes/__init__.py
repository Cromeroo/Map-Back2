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

    # Configurar CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:5174"}})

    # Configurar caché
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    db.init_app(app)

    from ..weather_api import weather_api
    app.register_blueprint(weather_api, url_prefix='/api')

    from .main_routes import main_routes
    app.register_blueprint(main_routes)

    from .auth_routes import auth_routes
    app.register_blueprint(auth_routes, url_prefix='/auth')

    return app