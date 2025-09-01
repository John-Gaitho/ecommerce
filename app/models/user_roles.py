# app/models/user_role.py
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db


class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationship to User
    users = db.relationship("User", back_populates="role", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
        }

    def __repr__(self):
        return f"<UserRole {self.name}>"
