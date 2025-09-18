from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def roles_required(*roles):
    """
    Restrict access to users with specific roles.
    Usage:
        @roles_required("admin")
        @roles_required("admin", "customer")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in roles:
                return jsonify({"message": "Forbidden"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
