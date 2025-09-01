from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.contact_message import ContactMessage

contact_bp = Blueprint("contact", __name__, url_prefix="/contact")

@contact_bp.route("/", methods=["POST"])
def create_contact_message():
    data = request.get_json()
    if not data or not all(key in data for key in ("name", "email", "subject", "message")):
        return jsonify({"error": "Missing required fields"}), 400

    message = ContactMessage(
        name=data["name"],
        email=data["email"],
        subject=data["subject"],
        message=data["message"]
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({"message": "Contact message created successfully"}), 201
