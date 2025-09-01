from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, UserRole
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    address = data.get("address")

    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_already_registered"}), 400

    user = User(email=email, first_name=first_name, last_name=last_name,
                phone_number=phone_number, address=address)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # default role
    role = UserRole(user_id=user.id, role="customer")
    db.session.add(role)
    db.session.commit()

    return jsonify({"message": "registered_successfully"}), 201

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials"}), 401

    roles = [r.role for r in user.roles]
    access = create_access_token(identity=str(user.id), additional_claims={"roles": roles}, expires_delta=timedelta(hours=12))
    return jsonify({"access_token": access, "roles": roles})

@auth_bp.get("/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({"error": "not_found"}), 404
    return jsonify({
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "address": user.address,
        "roles": [r.role for r in user.roles]
    })