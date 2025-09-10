import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum


class UserRole(Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(
        db.Enum(UserRole, name="user_role"),
        default=UserRole.CUSTOMER,
        nullable=False,
    )

    # ✅ Relationships
    profile = db.relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", back_populates="user", cascade="all, delete-orphan")

    # --- Helper properties ---
    @property
    def is_admin(self):
        """Check if the user is an admin"""
        return self.role == UserRole.ADMIN

    # --- Serialization ---
    def to_dict(self, include_profile=False):
        data = {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "role": self.role.value if self.role else None,
            "is_admin": self.is_admin,  # optional convenience
        }
        if include_profile and self.profile:
            data["profile"] = self.profile.to_dict()
        return data

    def __repr__(self):
        return f"<User {self.email}>"
