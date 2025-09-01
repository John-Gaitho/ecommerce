from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from app.models import UserRole

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            uid = get_jwt_identity()
            has = UserRole.query.filter_by(user_id=uid).filter(UserRole.role.in_(roles)).first()
            if not has:
                return jsonify({"message": "Forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
