from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import content_controller as ctrl
from app.middleware.rbac import admin_required

bp = Blueprint("content", __name__, url_prefix="/api")


@bp.route("/homepage", methods=["GET"])
def homepage():
    return ctrl.homepage()


@bp.route("/news", methods=["GET"])
def list_news():
    return ctrl.list_news()


@bp.route("/news/<slug_or_id>", methods=["GET"])
def get_news(slug_or_id):
    return ctrl.get_news(slug_or_id)


@bp.route("/news", methods=["POST"])
@jwt_required()
@admin_required
def create_news():
    return ctrl.create_news()


@bp.route("/news/<article_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_news(article_id):
    return ctrl.update_news(article_id)


@bp.route("/news/<article_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_news(article_id):
    return ctrl.delete_news(article_id)


@bp.route("/courses", methods=["GET"])
def list_courses():
    return ctrl.list_courses()


@bp.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):
    return ctrl.get_course(course_id)


@bp.route("/courses", methods=["POST"])
@jwt_required()
@admin_required
def create_course():
    return ctrl.create_course()


@bp.route("/courses/<course_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_course(course_id):
    return ctrl.update_course(course_id)


@bp.route("/courses/<course_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_course(course_id):
    return ctrl.delete_course(course_id)


@bp.route("/contact", methods=["POST"])
def submit_contact():
    return ctrl.submit_contact()


@bp.route("/contact", methods=["GET"])
@jwt_required()
@admin_required
def list_contacts():
    return ctrl.list_contacts()


@bp.route("/contact/<contact_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_contact(contact_id):
    return ctrl.get_contact(contact_id)


@bp.route("/contact/<contact_id>", methods=["PATCH"])
@jwt_required()
@admin_required
def update_contact_status(contact_id):
    return ctrl.update_contact_status(contact_id)


@bp.route("/contact/<contact_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_contact(contact_id):
    return ctrl.delete_contact(contact_id)


@bp.route("/seo/<page_key>", methods=["GET"])
def get_seo(page_key):
    return ctrl.get_seo(page_key)


@bp.route("/seo", methods=["GET"])
@jwt_required()
@admin_required
def list_seo():
    return ctrl.list_seo()


@bp.route("/seo/<page_key>", methods=["PUT"])
@jwt_required()
@admin_required
def update_seo(page_key):
    return ctrl.update_seo(page_key)
