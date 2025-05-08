from flask import Blueprint, jsonify, request
from sqlalchemy import text  # Importa text()
import os
import mysql.connector
from app import db
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models.ContenidoPagina import ContenidoPagina

main_routes = Blueprint("main_routes", __name__)

@main_routes.route("/")
def home():
    return jsonify({"message": "✅ Flask está funcionando correctamente"}), 200

@main_routes.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 204

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

@main_routes.route("/admin-only")
@jwt_required()
def admin_only():
    claims = get_jwt()
    role = claims.get("role")
    if role != "admin":
        return jsonify({"error": "No autorizado"}), 403
    return jsonify({"message": "Bienvenido, admin"})

@main_routes.route("/contenido/<seccion>", methods=["GET"])
def obtener_contenido(seccion):
    textos = ContenidoPagina.query.filter_by(seccion=seccion).all()
    return jsonify([
        {"id": t.id, "tipo": t.tipo, "contenido": t.contenido}
        for t in textos
    ])

# Modificar un texto (solo admin)
@main_routes.route("/contenido/<int:id>", methods=["PUT"])
@jwt_required()
def editar_contenido(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()
    texto = ContenidoPagina.query.get_or_404(id)
    texto.contenido = data.get("contenido", texto.contenido)
    db.session.commit()
    return jsonify({"message": "Contenido actualizado"})

# Crear un nuevo texto (solo admin)
@main_routes.route("/contenido", methods=["POST"])
@jwt_required()
def crear_contenido():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()
    nuevo = ContenidoPagina(
        seccion=data["seccion"],
        tipo=data["tipo"],
        contenido=data["contenido"]
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"message": "Contenido creado", "id": nuevo.id}), 201

# Borrar un texto (solo admin)
@main_routes.route("/contenido/<int:id>", methods=["DELETE"])
@jwt_required()
def borrar_contenido(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    texto = ContenidoPagina.query.get_or_404(id)
    db.session.delete(texto)
    db.session.commit()
    return jsonify({"message": "Contenido eliminado"})