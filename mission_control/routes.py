from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from mission_control.extensions import db
from mission_control.models import User

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return jsonify({"message": "Mission Control API is operational", "status": "online"})

@main_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@main_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "code": "INVALID_JSON",
            "message": "Request body must be a valid JSON object"
        }), 400

    if "email" not in data:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "email is required"
        }), 400

    if "password" not in data:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "password is required"
        }), 400

    email = data["email"]
    password = data["password"]

    if not isinstance(email, str):
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "email must be a string"
        }), 400

    if not isinstance(password, str):
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "password must be a string"
        }), 400

    email = email.strip()

    if len(email) < 3 or len(email) > 254:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "email must be between 3 and 254 characters"
        }), 400

    if len(password) < 8 or len(password) > 128:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "password must be between 8 and 128 characters"
        }), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "code": "DUPLICATE_EMAIL",
            "message": "email is already registered"
        }), 409

    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 201
