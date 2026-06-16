from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import dashboard_controller as ctrl
from app.middleware.rbac import admin_required, teacher_required, student_required

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.route("/admin", methods=["GET"])
@jwt_required()
@admin_required
def admin_dashboard():
    return ctrl.admin_dashboard()


@bp.route("/teacher", methods=["GET"])
@jwt_required()
@teacher_required
def teacher_dashboard():
    return ctrl.teacher_dashboard()


@bp.route("/student", methods=["GET"])
@jwt_required()
@student_required
def student_dashboard():
    return ctrl.student_dashboard()
