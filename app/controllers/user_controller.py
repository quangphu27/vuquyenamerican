from flask import request, jsonify
from app.services.user_service import UserService

user_service = UserService()


def list_teachers():
    page = request.args.get("page", 1)
    return jsonify(user_service.list_teachers(int(page))), 200


def list_students():
    page = request.args.get("page", 1)
    status = request.args.get("status")
    return jsonify(user_service.list_students(status, int(page))), 200


def create_teacher():
    data = request.get_json() or {}
    result, error = user_service.create_teacher(data)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 201


def update_student_status(student_id):
    data = request.get_json() or {}
    result, error = user_service.update_student_status(student_id, data.get("status"))
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 200


def update_teacher_status(teacher_id):
    data = request.get_json() or {}
    result, error = user_service.update_teacher_status(teacher_id, data.get("status"))
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 200


def update_user(user_id):
    data = request.get_json() or {}
    role = request.args.get("role", "student")
    result, error = user_service.update_user(user_id, role, data)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 200


def delete_user(user_id):
    role = request.args.get("role", "student")
    user_service.delete_user(user_id, role)
    return jsonify({"message": "Đã xóa"}), 200
