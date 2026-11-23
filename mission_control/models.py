from datetime import datetime, timezone
from mission_control.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
        nullable=False,
    )

    role = db.Column(db.String(50), nullable=False, default="user", server_default="user")
    missions = db.relationship("Mission", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class Mission(db.Model):
    __tablename__ = "missions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="missions")
    title = db.Column(db.String(150), nullable=False)

    destination = db.Column(db.String(150), nullable=False)
    launch_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="planned", server_default="planned")
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<Mission {self.title} (Status: {self.status})>"


