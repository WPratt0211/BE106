from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return jsonify({"message": "Mission Control API is operational", "status": "online"})
