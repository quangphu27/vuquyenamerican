from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in roles:
                return jsonify({"message": "Không có quyền truy cập"}), 403

            from app.services.auth_service import AuthService
            status_error = AuthService().validate_session_user(get_jwt_identity(), user_role)
            if status_error:
                return jsonify({"message": status_error}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn):
    return role_required("admin")(fn)


def teacher_required(fn):
    return role_required("admin", "teacher")(fn)


def student_required(fn):
    return role_required("admin", "teacher", "student")(fn)
