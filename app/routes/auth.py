from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models.user import User, UserRole
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from app.utils.jwt_utils import roles_required  # ✅ custom decorator

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# --- Register ---
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
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
        role=UserRole.CUSTOMER,  # default role
    )

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # ✅ Include role in JWT
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value}
    )

    return jsonify(
        {
            "access_token": token,
            "user": user.to_dict(),
        }
    ), 201

# --- Login ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # ✅ Include role in JWT
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value}
    )

    return jsonify(
        {
            "access_token": token,
            "user": user.to_dict(),
        }
    ), 200

# --- Me ---
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200

# --- Promote to Admin ---
@auth_bp.route("/promote/<uuid:user_id>", methods=["PATCH"])
@jwt_required()
@roles_required("admin")  # ✅ now works via JWT claims
def promote(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role = UserRole.ADMIN
    db.session.commit()

    return jsonify({"message": f"{user.email} promoted to ADMIN"}), 200

# --- Get Role ---
@auth_bp.route("/role", methods=["GET"])
@jwt_required()
def get_role():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"role": user.role.value}), 200
