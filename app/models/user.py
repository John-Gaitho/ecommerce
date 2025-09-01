import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db, bcrypt


class UserRole(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", lazy=True, cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", back_populates="user", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", lazy=True, cascade="all, delete-orphan")

    # Password helpers
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self, include_profile=False):
        data = {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_profile and self.profile:
            data["profile"] = self.profile.to_dict()
        return data

    def __repr__(self):
        return f"<User {self.email}>"
