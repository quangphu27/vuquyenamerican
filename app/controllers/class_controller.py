from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.services.class_service import ClassService

class_service = ClassService()


def list_classes():
    page = request.args.get("page", 1)
    teacher_id = request.args.get("teacher_id")
    claims = get_jwt()
    if claims.get("role") == "teacher" and not teacher_id:
        teacher_id = get_jwt_identity()
    return jsonify(class_service.list_classes(teacher_id, int(page))), 200


def get_class(class_id):
    cls = class_service.get_class(class_id)
    if not cls:
        return jsonify({"message": "Không tìm thấy lớp"}), 404
    return jsonify(cls), 200


def create_class():
    data = request.get_json() or {}
    claims = get_jwt()
    teacher_id = data.get("teacher_id") or (
        get_jwt_identity() if claims.get("role") == "teacher" else None
    )
    if not teacher_id:
        return jsonify({"message": "Vui lòng chọn giáo viên"}), 400
    if not data.get("name", "").strip():
        return jsonify({"message": "Tên lớp là bắt buộc"}), 400
    cls = class_service.create_class(data, teacher_id)
    return jsonify(cls), 201


def update_class(class_id):
    data = request.get_json() or {}
    cls = class_service.update_class(class_id, data)
    return jsonify(cls), 200


def add_student(class_id):
    data = request.get_json() or {}
    result, error = class_service.add_student(class_id, data["student_id"])
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 200


def remove_student(class_id):
    data = request.get_json() or {}
    result, error = class_service.remove_student(class_id, data["student_id"])
    return jsonify(result), 200


def transfer_student():
    data = request.get_json() or {}
    result, error = class_service.transfer_student(
        data["from_class_id"], data["to_class_id"], data["student_id"]
    )
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 200


def delete_class(class_id):
    class_service.delete_class(class_id)
    return jsonify({"message": "Đã xóa lop"}), 200
