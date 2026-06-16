from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import user_controller as ctrl
from app.middleware.rbac import admin_required, teacher_required

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.route("/teachers", methods=["GET"])
@jwt_required()
@admin_required
def list_teachers():
    return ctrl.list_teachers()


@bp.route("/teachers", methods=["POST"])
@jwt_required()
@admin_required
def create_teacher():
    return ctrl.create_teacher()


@bp.route("/students", methods=["GET"])
@jwt_required()
@teacher_required
def list_students():
    return ctrl.list_students()


@bp.route("/students/<student_id>/status", methods=["PATCH"])
@jwt_required()
@admin_required
def update_student_status(student_id):
    return ctrl.update_student_status(student_id)


@bp.route("/teachers/<teacher_id>/status", methods=["PATCH"])
@jwt_required()
@admin_required
def update_teacher_status(teacher_id):
    return ctrl.update_teacher_status(teacher_id)


@bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    return ctrl.update_user(user_id)


@bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    return ctrl.delete_user(user_id)
