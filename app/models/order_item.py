import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": str(self.id),
            "order_id": str(self.order_id),
            "product_id": str(self.product_id),
            "quantity": self.quantity,
            "price": self.price,
        }

    def __repr__(self):
        return f"<OrderItem {self.id}>"
