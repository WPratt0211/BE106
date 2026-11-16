from werkzeug.security import generate_password_hash, check_password_hash
from mission_control import create_app
from mission_control.models import User

def test_password_hashing_audit():
    app = create_app("development")
    with app.app_context():
        user = User.query.filter_by(email="pilot@example.com").first()
        if user:
            # Audit 1: Verify hash prefix is modern secure algorithm
            assert user.password_hash.startswith("scrypt:")
            # Audit 2: Verify correct password matches
            assert check_password_hash(user.password_hash, "strong-pass-123") is True
            # Audit 3: Verify incorrect password fails
            assert check_password_hash(user.password_hash, "wrong-pass-999") is False

        # Audit 4: Verify generate_password_hash never produces plaintext
        raw_pwd = "test-secret-password"
        hashed = generate_password_hash(raw_pwd)
        assert hashed.startswith("scrypt:")
        assert raw_pwd not in hashed
        assert check_password_hash(hashed, raw_pwd) is True
        assert check_password_hash(hashed, "wrong-secret") is False


if __name__ == "__main__":
    test_password_hashing_audit()
    print("Password hashing audit passed successfully.")
