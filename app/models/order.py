import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db
from app.models.order_item import OrderItem  # import OrderItem

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self, include_items=True):
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "email": self.email,
            "total_amount": self.total_amount,
            "shipping_address": self.shipping_address,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data["items"] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self):
        return f"<Order {self.id}>"
