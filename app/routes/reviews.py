from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.review import Review

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.get("/product/<product_id>")
def list_reviews(product_id):
    items = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    return jsonify([serialize_review(r) for r in items])

@reviews_bp.post("/")
@jwt_required()
def add_review():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    r = Review(user_id=uid, product_id=data["product_id"], rating=int(data["rating"]), comment=data.get("comment"))
    if r.rating < 1 or r.rating > 5:
        return jsonify({"error": "rating_out_of_range"}), 400
    db.session.add(r)
    db.session.commit()
    return jsonify({"message": "created", "id": str(r.id)}), 201

def serialize_review(r: Review):
    return {
        "id": str(r.id),
        "user_id": str(r.user_id),
        "product_id": str(r.product_id),
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }