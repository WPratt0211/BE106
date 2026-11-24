from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from config import config_by_name
from mission_control.extensions import db, migrate
from mission_control.routes import main_bp
from mission_control.auth import auth_bp
from mission_control.missions import missions_bp
from mission_control import models

def register_error_handlers(app):
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            "code": "BAD_REQUEST",
            "message": getattr(e, "description", "Bad request")
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({
            "code": "UNAUTHORIZED",
            "message": getattr(e, "description", "Authentication required")
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({
            "code": "FORBIDDEN",
            "message": getattr(e, "description", "Access forbidden")
        }), 403

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "code": "NOT_FOUND",
            "message": getattr(e, "description", "Resource not found")
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({
            "code": "METHOD_NOT_ALLOWED",
            "message": getattr(e, "description", "Method not allowed")
        }), 405

    @app.errorhandler(500)
    def handle_internal_server_error(e):
        return jsonify({
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred"
        }), 500

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({
                "code": e.name.upper().replace(" ", "_"),
                "message": e.description
            }), e.code
        return jsonify({
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred"
        }), 500

def create_app(config_name="development"):
    app = Flask(__name__)

    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    register_error_handlers(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(missions_bp)

    return app
