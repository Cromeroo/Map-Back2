from flask import Blueprint, jsonify
from ..models.database import db

main_bp = Blueprint("main", __name__)

@main_bp.route("/ping")
def ping_db():
    try:
        db.engine.execute("SELECT 1")
        return jsonify({"message": "✅ Base de datos conectada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"❌ No se pudo conectar a la base de datos: {e}"}), 500
