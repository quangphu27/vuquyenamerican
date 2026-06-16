from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import document_controller as ctrl
from app.middleware.rbac import teacher_required, student_required

bp = Blueprint("documents", __name__, url_prefix="/api/documents")


@bp.route("", methods=["GET"])
@jwt_required()
def list_documents():
    return ctrl.list_documents()


@bp.route("/<doc_id>", methods=["GET"])
@jwt_required()
def get_document(doc_id):
    return ctrl.get_document(doc_id)


@bp.route("", methods=["POST"])
@jwt_required()
@teacher_required
def create_document():
    return ctrl.create_document()


@bp.route("/<doc_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_document(doc_id):
    return ctrl.update_document(doc_id)


@bp.route("/<doc_id>/download", methods=["POST"])
@jwt_required()
@student_required
def download_document(doc_id):
    return ctrl.download_document(doc_id)


@bp.route("/<doc_id>", methods=["DELETE"])
@jwt_required()
@teacher_required
def delete_document(doc_id):
    return ctrl.delete_document(doc_id)
