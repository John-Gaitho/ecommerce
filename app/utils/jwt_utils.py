from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from app.models.user import User, UserRole


def roles_required(*roles):
    """
    Restrict access to users with specific roles.
    Usage:
        @roles_required(UserRole.ADMIN)
        @roles_required(UserRole.ADMIN, UserRole.CUSTOMER)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            uid = get_jwt_identity()
            user = User.query.get(uid)

            if not user or user.role not in roles:
                return jsonify({"message": "Forbidden"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
