# app/routes/order_item.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.order_item import OrderItem
from app.models.order import Order
from app.models.product import Product
from app.models.user import User

order_items_bp = Blueprint("order_items", __name__, url_prefix="/order_items")


# --- Helper to serialize order items ---
def serialize_order_item(item):
    return {
        "id": str(item.id),
        "order_id": str(item.order_id),
        "product_id": str(item.product_id),
        "quantity": item.quantity,
        "price": item.price,
    }


# --- Routes ---
@order_items_bp.route("/", methods=["GET", "POST"])
@jwt_required()
def order_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if request.method == "GET":
        if not user or not user.is_admin:
            items = OrderItem.query.join(Order).filter(Order.user_id == current_user_id).all()
        else:
            items = OrderItem.query.all()
        return jsonify([serialize_order_item(i) for i in items])

    if request.method == "POST":
        data = request.json

        order = Order.query.get_or_404(data["order_id"])
        if order.user_id != current_user_id:
            if not user or not user.is_admin:
                return jsonify({"error": "You do not have permission to modify this order"}), 403

        product = Product.query.get(data["product_id"])
        if not product:
            return jsonify({"error": f"Product {data['product_id']} not found"}), 404

        item = OrderItem(
            order_id=data["order_id"],
            product_id=data["product_id"],
            quantity=data.get("quantity", 1),
            price=product.price
        )

        try:
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400

        return jsonify(serialize_order_item(item)), 201


@order_items_bp.route("/<uuid:item_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def order_item_detail(item_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    item = OrderItem.query.get_or_404(item_id)

    if request.method == "GET":
        if item.order.user_id != current_user_id and not (user and user.is_admin):
            return jsonify({"error": "You do not have permission to view this item"}), 403
        return jsonify(serialize_order_item(item))

    if request.method == "PUT":
        if item.order.user_id != current_user_id and not (user and user.is_admin):
            return jsonify({"error": "You do not have permission to update this item"}), 403

        data = request.json
        if "quantity" in data:
            item.quantity = data["quantity"]
        if "price" in data:
            item.price = data["price"]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400

        return jsonify(serialize_order_item(item))

    if request.method == "DELETE":
        if item.order.user_id != current_user_id and not (user and user.is_admin):
            return jsonify({"error": "You do not have permission to delete this item"}), 403

        try:
            db.session.delete(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400

        return jsonify({"message": "Order item deleted"}), 200
