from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.review import Review
from app.utils.decorators import roles_required  # your decorator
from app.models.user import UserRole

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")

# --- List reviews for a product ---
@reviews_bp.get("/product/<string:product_id>")
def list_reviews(product_id):
    items = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    return jsonify([serialize_review(r) for r in items]), 200

# --- Add a review (authenticated users) ---
@reviews_bp.post("/")
@jwt_required()
def add_review():
    uid = get_jwt_identity()
    data = request.get_json() or {}

    rating = data.get("rating")
    product_id = data.get("product_id")
    comment = data.get("comment", "")

    if not rating or not product_id:
        return jsonify({"error": "product_id and rating required"}), 400

    if int(rating) < 1 or int(rating) > 5:
        return jsonify({"error": "rating must be between 1 and 5"}), 400

    r = Review(user_id=uid, product_id=product_id, rating=int(rating), comment=comment)
    db.session.add(r)
    db.session.commit()
    return jsonify({"message": "created", "id": str(r.id)}), 201

# --- Delete a review (admin only) ---
@reviews_bp.delete("/<string:review_id>")
@jwt_required()
@roles_required(UserRole.ADMIN)
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"}), 200

# --- Helper: Serialize a review ---
def serialize_review(r: Review):
    return {
        "id": str(r.id),
        "user_id": str(r.user_id),
        "product_id": str(r.product_id),
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
