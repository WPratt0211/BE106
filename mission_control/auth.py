from datetime import datetime, timezone, timedelta
import functools
import jwt
from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from mission_control.extensions import db
from mission_control.models import User

auth_bp = Blueprint("auth", __name__)

def jwt_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "code": "UNAUTHORIZED",
                "message": "Authorization token required"
            }), 401

        token = auth_header.split(" ", 1)[1].strip()
        secret = current_app.config.get("JWT_SECRET")

        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({
                "code": "TOKEN_EXPIRED",
                "message": "Authentication token has expired"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "code": "INVALID_TOKEN",
                "message": "Invalid authentication token"
            }), 401

        sub = payload.get("sub")
        if not sub:
            return jsonify({
                "code": "INVALID_TOKEN",
                "message": "Invalid authentication token"
            }), 401

        try:
            user_id = int(sub)
        except (ValueError, TypeError):
            return jsonify({
                "code": "INVALID_TOKEN",
                "message": "Invalid authentication token"
            }), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "code": "UNAUTHORIZED",
                "message": "User not found"
            }), 401


        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function

@auth_bp.route("/register", methods=["POST"])
@auth_bp.route("/auth/register", methods=["POST"])
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

@auth_bp.route("/login", methods=["POST"])
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "code": "INVALID_JSON",
            "message": "Request body must be a valid JSON object"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "code": "UNAUTHORIZED",
            "message": "Invalid email or password"
        }), 401

    user = User.query.filter_by(email=email.strip()).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({
            "code": "UNAUTHORIZED",
            "message": "Invalid email or password"
        }), 401

    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not configured")
    lifetime_minutes = current_app.config.get("JWT_EXPIRATION_MINUTES", 60)
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=lifetime_minutes)

    payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@auth_bp.route("/auth/profile", methods=["GET"])
@jwt_required
def profile():
    user = g.current_user
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 200
