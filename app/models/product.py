# app/models/product.py

from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
import uuid
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)  # legacy / fallback main image
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
    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True
    )
    reviews = db.relationship(
        "Review",
        back_populates="product",
        lazy=True,
        cascade="all, delete-orphan"
    )
    order_items = db.relationship(
        "OrderItem",
        back_populates="product",
        lazy=True,
        cascade="all, delete-orphan"
    )
    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self, include_relationships=False):
        """Serialize product with multiple Cloudinary images + fallback."""
        data = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url or "/static/default_product.png",
            "images": [img.to_dict() for img in self.images],  # new
            "slug": self.slug,
            "category": self.category,
            "price": float(self.price) if self.price is not None else 0.0,
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


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String, nullable=False)
    public_id = db.Column(db.String, nullable=False)  # needed to delete from Cloudinary
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey("products.id"), nullable=False)

    product = db.relationship("Product", back_populates="images")

    def to_dict(self):
        return {
            "id": str(self.id),
            "url": self.url,
            "public_id": self.public_id,
        }

    def __repr__(self):
        return f"<ProductImage {self.url}>"
