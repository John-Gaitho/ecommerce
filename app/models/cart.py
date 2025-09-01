import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user = db.relationship("User", back_populates="cart_items")
    product = db.relationship("Product", back_populates="cart_items")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "product_id": str(self.product_id),
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
