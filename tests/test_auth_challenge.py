from mission_control import create_app

from mission_control.models import User
from mission_control.extensions import db

def test_auth_attack_suite():
    app = create_app("development")
    client = app.test_client()

    # Obtain valid non-admin token
    res = client.post("/auth/login", json={"email": "pilot_updated@example.com", "password": "strong-pass-123"})
    token = res.get_json()["token"]

    # Attack 1: Missing Token
    r1 = client.get("/auth/profile")
    assert r1.status_code == 401
    assert r1.get_json()["code"] == "UNAUTHORIZED"

    # Attack 2: Tampered Signature
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    r2 = client.get("/auth/profile", headers={"Authorization": f"Bearer {tampered}"})
    assert r2.status_code == 401
    assert r2.get_json()["code"] == "INVALID_TOKEN"

    # Attack 3: Privilege Escalation
    r3 = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 403
    assert r3.get_json()["code"] == "FORBIDDEN"

    # Attack 4: ID Injection via Body
    r4 = client.patch("/auth/profile", headers={"Authorization": f"Bearer {token}"}, json={"id": 2, "email": "takeover@example.com"})
    assert r4.status_code == 400
    assert r4.get_json()["code"] == "INVALID_FIELD"

    # Attack 5: Duplicate Email Account Takeover
    r5 = client.patch("/auth/profile", headers={"Authorization": f"Bearer {token}"}, json={"email": "commander_updated@example.com"})
    assert r5.status_code == 409
    assert r5.get_json()["code"] == "DUPLICATE_EMAIL"

if __name__ == "__main__":
    test_auth_attack_suite()
    print("All auth defense checks passed.")
