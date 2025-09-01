# app/models/review.py
import uuid
from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey("products.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship("Product", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")   # ✅ added

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "product_id": str(self.product_id),
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Review {self.rating} stars>"
