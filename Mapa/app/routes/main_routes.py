from flask import Blueprint, jsonify
from ..models.database import db
from sqlalchemy import text  # Importa text()
import os
import mysql.connector
from app import db

main_routes = Blueprint("main_routes", __name__)

@main_routes.route("/")
def home():
    return jsonify({"message": "✅ Flask está funcionando correctamente"}), 200


@main_routes.route("/ping-db")
def ping_db():
    """Prueba la conexión a la base de datos con SQLAlchemy"""
    print("🔍 Iniciando prueba de conexión con SQLAlchemy en Flask...")
    try:
        with db.engine.connect() as connection:
            print("✅ Conexión establecida con SQLAlchemy en Flask")
            result = connection.execute(text("SELECT 1"))
            print("🔍 Resultado de consulta:", result.scalar())
            return jsonify({"message": "✅ Conexión exitosa a la base de datos"}), 200
    except Exception as e:
        print(f"❌ ERROR en la conexión: {e}")
        return jsonify({"error": f"❌ Error en la conexión: {str(e)}"}), 500