from datetime import datetime, timezone, timedelta
from mission_control import create_app
from mission_control.models import User, Mission
from mission_control.extensions import db

def test_read_mission_by_id():
    app = create_app("development")
    client = app.test_client()

    # Log in User A and User B
    res_a = client.post("/auth/login", json={"email": "pilot_updated@example.com", "password": "strong-pass-123"})
    token_a = res_a.get_json()["token"]

    res_b = client.post("/auth/login", json={"email": "commander_updated@example.com", "password": "strong-pass-456"})
    token_b = res_b.get_json()["token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    with app.app_context():
        user_a = User.query.filter_by(email="pilot_updated@example.com").first()
        user_b = User.query.filter_by(email="commander_updated@example.com").first()
        mission_a = Mission.query.filter_by(user_id=user_a.id).first()
        mission_b = Mission.query.filter_by(user_id=user_b.id).first()

    # 1. Existing ID owned by caller -> 200
    r1 = client.get(f"/missions/{mission_a.id}", headers=headers_a)
    assert r1.status_code == 200
    assert r1.get_json()["id"] == mission_a.id

    # 2. Nonexistent ID -> 404
    r2 = client.get("/missions/999999", headers=headers_a)
    assert r2.status_code == 404
    assert r2.get_json()["code"] == "NOT_FOUND"

    # 3. Another user's mission ID -> 403
    r3 = client.get(f"/missions/{mission_b.id}", headers=headers_a)
    assert r3.status_code == 403
    assert r3.get_json()["code"] == "FORBIDDEN"

if __name__ == "__main__":
    test_read_mission_by_id()
    print("Mission read-by-ID tests passed successfully.")
