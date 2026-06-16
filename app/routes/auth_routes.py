from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import auth_controller as ctrl
from app.extensions import limiter

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    return ctrl.login()


@bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    return ctrl.register()


@bp.route("/refresh", methods=["POST"])
def refresh():
    return ctrl.refresh()


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    return ctrl.me()


@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    return ctrl.update_profile()


@bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    return ctrl.change_password()
