from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService

auth_service = AuthService()


def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"message": "Email và mật khẩu là bắt buộc"}), 400
    result, error = auth_service.login(email, password)
    if error:
        return jsonify({"message": error}), 401
    return jsonify(result), 200


def register():
    data = request.get_json() or {}
    required = ["email", "password", "full_name"]
    field_labels = {"email": "Email", "password": "Mật khẩu", "full_name": "Họ tên"}
    for field in required:
        if not data.get(field):
            label = field_labels.get(field, field)
            return jsonify({"message": f"{label} là bắt buộc"}), 400
    if len(data["password"]) < 6:
        return jsonify({"message": "Mật khẩu tối thiểu 6 ký tự"}), 400
    result, error = auth_service.register_student(data)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Đăng ký thành công. Vui lòng chờ admin duyệt.", "user": result}), 201


@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    claims = get_jwt()
    token, error = auth_service.refresh(user_id, claims)
    if error:
        return jsonify({"message": error}), 403
    return jsonify({"access_token": token}), 200


@jwt_required()
def me():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    status_error = auth_service.validate_session_user(user_id, role)
    if status_error:
        return jsonify({"message": status_error}), 403
    user = auth_service.get_user_by_id(user_id, role)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404
    return jsonify(user), 200


@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    status_error = auth_service.validate_session_user(user_id, role)
    if status_error:
        return jsonify({"message": status_error}), 403
    data = request.get_json() or {}
    if not data.get("full_name", "").strip():
        return jsonify({"message": "Họ tên là bắt buộc"}), 400
    user, error = auth_service.update_profile(user_id, role, data)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(user), 200


@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    status_error = auth_service.validate_session_user(user_id, role)
    if status_error:
        return jsonify({"message": status_error}), 403
    data = request.get_json() or {}
    user, error = auth_service.change_password(
        user_id,
        role,
        data.get("current_password", ""),
        data.get("new_password", ""),
    )
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Đổi mật khẩu thành công", "user": user}), 200
