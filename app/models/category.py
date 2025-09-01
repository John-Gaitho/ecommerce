from app.extensions import db
from datetime import datetime
from app.utils import generate_uuid


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    products = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"
