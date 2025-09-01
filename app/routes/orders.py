from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.order import Order
from app.models.user import User

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


# --- Helper function to serialize orders ---
def serialize_order(order):
    return {
        "id": str(order.id),
        "user_id": str(order.user_id),
        "status": order.status,
        "total_price": order.total_price,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


# --- Routes ---
@orders_bp.route("/", methods=["GET", "POST"])
@jwt_required()
def orders():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if request.method == "GET":
        if not user or not user.is_admin:
            orders = Order.query.filter_by(user_id=current_user_id).all()
        else:
            orders = Order.query.all()
        return jsonify([serialize_order(o) for o in orders])

    if request.method == "POST":
        data = request.json
        if data["user_id"] != str(current_user_id):
            if not user or not user.is_admin:
                return jsonify({"error": "You cannot create an order for another user"}), 403

        order = Order(
            user_id=data["user_id"],
            status=data.get("status", "pending"),
            total_price=data.get("total_price", 0.0),
        )
        try:
            db.session.add(order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400

        return jsonify(serialize_order(order)), 201


@orders_bp.route("/<uuid:order_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def order_detail(order_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    order = Order.query.get_or_404(order_id)

    if request.method == "GET":
        if order.user_id != current_user_id and not (user and user.is_admin):
            return jsonify({"error": "You do not have permission to view this order"}), 403
        return jsonify(serialize_order(order))

    if request.method == "PUT":
        if order.user_id != current_user_id and not (user and user.is_admin):
            return jsonify({"error": "You do not have permission to update this order"}), 403

        data = request.json
        if "status" in data:
            order.status = data["status"]
        if "total_price" in data:
            order.total_price = data["total_price"]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400

        return jsonify(serialize_order(order))

    if request.method == "DELETE":
        if order.user_id != current_user_id and not (user and user.is_admin):
            return jsonify({"error": "You do not have permission to delete this order"}), 403
        try:
            db.session.delete(order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400
        return jsonify({"message": "Order deleted"}), 200
