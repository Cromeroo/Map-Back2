from flask_sqlalchemy import SQLAlchemy

# Inicializamos la base de datos
db = SQLAlchemy()

def init_db(app):
    """Inicializa la base de datos con la aplicación Flask"""
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
