from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from app.extensions import db
from app.models.contact_message import ContactMessage

contact_bp = Blueprint("contact", __name__)

# --- Helper: Admin-only decorator ---
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admins only"}), 403
        return fn(*args, **kwargs)
    return wrapper

# --- Create Contact Message (Public) ---
@contact_bp.route("/", methods=["POST"])
def create_contact_message():
    data = request.get_json()
    if not data or not all(key in data for key in ("name", "email", "subject", "message")):
        return jsonify({"error": "Missing required fields"}), 400

    message = ContactMessage(
        name=data["name"],
        email=data["email"],
        subject=data["subject"],
        message=data["message"],
        status="unread"
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({"message": "Contact message created successfully"}), 201

# --- List All Contact Messages (Admin only) ---
@contact_bp.route("/", methods=["GET"])
@admin_required
def list_contact_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200

# --- Get Single Message by ID (Admin only) ---
@contact_bp.route("/<string:message_id>", methods=["GET"])
@admin_required
def get_contact_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    return jsonify(message.to_dict()), 200

# --- Update Message (Mark as Read, Admin only) ---
@contact_bp.route("/<string:message_id>", methods=["PUT"])
@admin_required
def update_contact_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    data = request.get_json()
    if "status" in data:
        message.status = data["status"]
    db.session.commit()
    return jsonify(message.to_dict()), 200

# --- Delete a Message (Admin only) ---
@contact_bp.route("/<string:message_id>", methods=["DELETE"])
@admin_required
def delete_contact_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({"message": "Contact message deleted successfully"}), 200
