from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.cart import CartItem
from app.models.product import Product

cart_bp = Blueprint("cart", __name__)

@cart_bp.get("/")
@jwt_required()
def get_cart():
    uid = get_jwt_identity()
    items = CartItem.query.filter_by(user_id=uid).all()
    return jsonify([serialize_cart(i) for i in items])

@cart_bp.post("/add")
@jwt_required()
def add_to_cart():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    product = Product.query.get_or_404(product_id)
    item = CartItem.query.filter_by(user_id=uid, product_id=product.id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=uid, product_id=product.id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return jsonify({"message": "added"})

@cart_bp.post("/update")
@jwt_required()
def update_cart():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    item_id = data.get("id")
    quantity = int(data.get("quantity", 1))

    item = CartItem.query.filter_by(id=item_id, user_id=uid).first_or_404()
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "updated"})

@cart_bp.delete("/<item_id>")
@jwt_required()
def remove_item(item_id):
    uid = get_jwt_identity()
    item = CartItem.query.filter_by(id=item_id, user_id=uid).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "removed"})

def serialize_cart(i: CartItem):
    return {
        "id": str(i.id),
        "product_id": str(i.product_id),
        "quantity": i.quantity,
        "product": {
            "name": i.product.name,
            "price": str(i.product.price),
            "image_url": i.product.image_url,
            "slug": i.product.slug,
        }
    }