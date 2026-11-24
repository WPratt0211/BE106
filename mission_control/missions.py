from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, g
from mission_control.extensions import db
from mission_control.models import Mission
from mission_control.auth import jwt_required

missions_bp = Blueprint("missions", __name__, url_prefix="/missions")

ALLOWED_UPDATE_FIELDS = {"title", "destination", "launch_date", "status"}

def serialize_mission(mission):
    return {
        "id": mission.id,
        "user_id": mission.user_id,
        "title": mission.title,
        "destination": mission.destination,
        "launch_date": mission.launch_date.isoformat() if mission.launch_date else None,
        "status": mission.status,
        "created_at": mission.created_at.isoformat() if mission.created_at else None,
    }

@missions_bp.route("", methods=["POST"])
@jwt_required
def create_mission():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "code": "INVALID_JSON",
            "message": "Request body must be a valid JSON object"
        }), 400

    # Ensure required fields are provided
    for field in ["title", "destination", "launch_date"]:
        if field not in data or not data[field]:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": f"{field} is required"
            }), 400

    title = str(data["title"]).strip()
    destination = str(data["destination"]).strip()
    launch_date_raw = data["launch_date"]

    if not title or len(title) > 150:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "title must be between 1 and 150 characters"
        }), 400

    if not destination or len(destination) > 150:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "destination must be between 1 and 150 characters"
        }), 400

    try:
        if isinstance(launch_date_raw, str):
            launch_date = datetime.fromisoformat(launch_date_raw.replace("Z", "+00:00"))
        else:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "launch_date must be a valid ISO format datetime string"
        }), 400

    status = str(data.get("status", "planned")).strip()

    # Server-assigned ownership strictly derived from authenticated user
    mission = Mission(
        user_id=g.current_user.id,
        title=title,
        destination=destination,
        launch_date=launch_date,
        status=status
    )
    db.session.add(mission)
    db.session.commit()

    return jsonify(serialize_mission(mission)), 201

@missions_bp.route("", methods=["GET"])
@jwt_required
def list_missions():
    # User-scoped list: caller only sees their own missions
    user_missions = Mission.query.filter_by(user_id=g.current_user.id).order_by(Mission.id.asc()).all()
    return jsonify({
        "missions": [serialize_mission(m) for m in user_missions],
        "count": len(user_missions)
    }), 200

@missions_bp.route("/<int:mission_id>", methods=["GET"])
@jwt_required
def get_mission(mission_id):
    mission = db.session.get(Mission, mission_id)
    if not mission:
        return jsonify({
            "code": "NOT_FOUND",
            "message": "Mission not found"
        }), 404

    # Enforce ownership isolation
    if mission.user_id != g.current_user.id:
        return jsonify({
            "code": "FORBIDDEN",
            "message": "Cannot access another user's mission"
        }), 403

    return jsonify(serialize_mission(mission)), 200

@missions_bp.route("/<int:mission_id>", methods=["PATCH"])
@jwt_required
def update_mission(mission_id):
    mission = db.session.get(Mission, mission_id)
    if not mission:
        return jsonify({
            "code": "NOT_FOUND",
            "message": "Mission not found"
        }), 404

    # Enforce ownership isolation
    if mission.user_id != g.current_user.id:
        return jsonify({
            "code": "FORBIDDEN",
            "message": "Cannot modify another user's mission"
        }), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "code": "INVALID_JSON",
            "message": "Request body must be a valid JSON object"
        }), 400

    disallowed_fields = set(data.keys()) - ALLOWED_UPDATE_FIELDS
    if disallowed_fields:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": f"Modification of fields not permitted: {', '.join(sorted(disallowed_fields))}"
        }), 400

    if "title" in data:
        title = str(data["title"]).strip()
        if not title or len(title) > 150:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": "title must be between 1 and 150 characters"
            }), 400
        mission.title = title

    if "destination" in data:
        dest = str(data["destination"]).strip()
        if not dest or len(dest) > 150:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": "destination must be between 1 and 150 characters"
            }), 400
        mission.destination = dest

    if "launch_date" in data:
        try:
            mission.launch_date = datetime.fromisoformat(str(data["launch_date"]).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": "launch_date must be a valid ISO format datetime string"
            }), 400

    if "status" in data:
        mission.status = str(data["status"]).strip()

    db.session.commit()
    return jsonify(serialize_mission(mission)), 200

@missions_bp.route("/<int:mission_id>", methods=["DELETE"])
@jwt_required
def delete_mission(mission_id):
    mission = db.session.get(Mission, mission_id)
    if not mission:
        return jsonify({
            "code": "NOT_FOUND",
            "message": "Mission not found"
        }), 404

    if mission.user_id != g.current_user.id:
        return jsonify({
            "code": "FORBIDDEN",
            "message": "Cannot delete another user's mission"
        }), 403

    db.session.delete(mission)
    db.session.commit()
    return jsonify({
        "code": "MISSION_DELETED",
        "message": "Mission successfully removed",
        "id": mission_id
    }), 200

