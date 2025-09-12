# app/utils/decorators.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from app.models.user import User, UserRole


def roles_required(*roles):
    """
    Restrict endpoint access to specific roles.
    Accepts either UserRole enums or strings like "admin", "customer".
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            uid = get_jwt_identity()
            user = User.query.get(uid)

            # Normalize roles: accept both Enum and str
            allowed_roles = []
            for r in roles:
                if isinstance(r, UserRole):
                    allowed_roles.append(r)
                elif isinstance(r, str):
                    try:
                        allowed_roles.append(UserRole[r.upper()])
                    except KeyError:
                        return jsonify({"message": f"Invalid role: {r}"}), 500

            # Check access
            if not user or user.role not in allowed_roles:
                return jsonify({"message": "Forbidden"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ✅ Backward-compatible alias
def role_required(role):
    return roles_required(role)
