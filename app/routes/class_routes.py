from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import class_controller as ctrl
from app.middleware.rbac import admin_required, teacher_required

bp = Blueprint("classes", __name__, url_prefix="/api/classes")


@bp.route("", methods=["GET"])
@jwt_required()
def list_classes():
    return ctrl.list_classes()


@bp.route("/<class_id>", methods=["GET"])
@jwt_required()
def get_class(class_id):
    return ctrl.get_class(class_id)


@bp.route("", methods=["POST"])
@jwt_required()
@teacher_required
def create_class():
    return ctrl.create_class()


@bp.route("/<class_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_class(class_id):
    return ctrl.update_class(class_id)


@bp.route("/<class_id>/students", methods=["POST"])
@jwt_required()
@teacher_required
def add_student(class_id):
    return ctrl.add_student(class_id)


@bp.route("/<class_id>/students", methods=["DELETE"])
@jwt_required()
@teacher_required
def remove_student(class_id):
    return ctrl.remove_student(class_id)


@bp.route("/transfer", methods=["POST"])
@jwt_required()
@teacher_required
def transfer_student():
    return ctrl.transfer_student()


@bp.route("/<class_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_class(class_id):
    return ctrl.delete_class(class_id)
