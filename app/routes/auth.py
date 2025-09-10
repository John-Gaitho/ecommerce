from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models.user import User, UserRole
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        email=email,
        password_hash=hashed_pw,
        name=name if name else "New User",
        role=UserRole.CUSTOMER,  # ✅ enum safe
    )

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    token = create_access_token(identity=str(user.id))

    return jsonify(
        {
            "access_token": token,
            "user": user.to_dict(),
        }
    ), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify(
        {
            "access_token": token,
            "user": user.to_dict(),
        }
    ), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# ✅ Admin promotion endpoint
@auth_bp.route("/promote/<uuid:user_id>", methods=["PATCH"])
@jwt_required()
def promote(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Admins only"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role = UserRole.ADMIN
    db.session.commit()

    return jsonify({"message": f"{user.email} promoted to ADMIN"}), 200

@auth_bp.route("/role", methods=["GET"])
@jwt_required()
def get_role():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"role": user.role.value}), 200