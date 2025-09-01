from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.product import Product
from app.utils.decorators import role_required
from flask_jwt_extended import jwt_required

products_bp = Blueprint("products", __name__)

@products_bp.get("/")
def list_products():
    q = Product.query
    category = request.args.get("category")
    if category:
        q = q.filter_by(category=category)
    featured = request.args.get("featured")
    if featured is not None:
        q = q.filter_by(is_featured=featured.lower() == "true")
    items = q.order_by(Product.created_at.desc()).all()
    return jsonify([serialize_product(p) for p in items])

@products_bp.get("/<slug>")
def get_by_slug(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    return jsonify(serialize_product(p))

@products_bp.post("/")
@jwt_required()
@role_required("admin")
def create_product():
    data = request.get_json() or {}
    p = Product(
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        image_url=data.get("image_url"),
        slug=data["slug"],
        category=data.get("category", "cups"),
        specifications=data.get("specifications", {}),
        stock_quantity=data.get("stock_quantity", 0),
        is_featured=data.get("is_featured", False),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"message": "created", "id": str(p.id)}), 201

@products_bp.put("/<slug>")
@jwt_required()
@role_required("admin")
def update_product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    data = request.get_json() or {}
    for field in ["name","description","price","image_url","category","specifications","stock_quantity","is_featured"]:
        if field in data:
            setattr(p, field, data[field])
    db.session.commit()
    return jsonify({"message": "updated"})

@products_bp.delete("/<slug>")
@jwt_required()
@role_required("admin")
def delete_product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "deleted"})

def serialize_product(p: Product):
    return {
        "id": str(p.id),
        "name": p.name,
        "description": p.description,
        "price": str(p.price),
        "image_url": p.image_url,
        "slug": p.slug,
        "category": p.category,
        "specifications": p.specifications or {},
        "stock_quantity": p.stock_quantity,
        "is_featured": p.is_featured,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }