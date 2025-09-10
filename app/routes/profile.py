from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.profile import Profile
from app.extensions import db

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("/", methods=["GET", "PUT"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Ensure profile exists
    if not user.profile:
        profile = Profile(
            user_id=user.id,
            first_name="",
            last_name="",
            phone_number="",
            address="",
            bio="",
            avatar_url=""
        )
        db.session.add(profile)
        db.session.commit()
        user.refresh()  # reload user.profile
    else:
        profile = user.profile

    # GET profile
    if request.method == "GET":
        return jsonify(profile.to_dict()), 200

    # PUT profile (update)
    if request.method == "PUT":
        data = request.json or {}

        allowed_fields = ["first_name", "last_name", "phone_number", "address", "bio", "avatar_url"]

        for field in allowed_fields:
            # Ensure all fields are strings, never None
            if field in data:
                setattr(profile, field, data[field] if data[field] is not None else "")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 400

        return jsonify(profile.to_dict()), 200
