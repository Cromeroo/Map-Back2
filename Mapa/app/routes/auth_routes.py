from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 204

@auth_routes.route("/register", methods=["POST"])
def register():
    """Registra un nuevo usuario"""
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario registrado exitosamente"}), 201

@auth_routes.route("/login", methods=["POST"])
def login():
    """Autentica un usuario y devuelve un token JWT"""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # Ejemplo recomendado:
    access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role}
)
    return jsonify({"token": access_token, "message": "Inicio de sesión exitoso"}), 200
