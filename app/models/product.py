from app.extensions import db 
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Product(db.Model):

    __tablename__ = "products"

    #id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    category = db.Column(db.String(100), default="cups")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    specifications = db.Column(MutableDict.as_mutable(JSONB), default=dict)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    # Relationships
    reviews = db.relationship("Review", back_populates="product", lazy=True, cascade="all, delete-orphan")
    order_items = db.relationship("OrderItem", back_populates="product", lazy=True, cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", back_populates="product", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_relationships=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "slug": self.slug,
            "category": self.category,
            "price": float(self.price),  # cast Decimal -> float for JSON
            "stock_quantity": self.stock_quantity,
            "is_featured": self.is_featured,
            "specifications": self.specifications,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relationships:
            data["reviews"] = [review.to_dict() for review in self.reviews]
            data["order_items"] = [item.to_dict() for item in self.order_items]
            data["cart_items"] = [item.to_dict() for item in self.cart_items]

        return data

    def __repr__(self):
        return f"<Product {self.name} - {self.slug}>"
