from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.document_service import DocumentService

doc_service = DocumentService()


def list_documents():
    page = request.args.get("page", 1)
    keyword = request.args.get("q", "")
    class_filter = request.args.get("class")
    return jsonify(doc_service.list_documents(keyword, class_filter, int(page))), 200


def get_document(doc_id):
    doc = doc_service.get_document(doc_id)
    if not doc:
        return jsonify({"message": "Không tìm thấy tài liệu"}), 404
    return jsonify(doc), 200


def create_document():
    data = request.form.to_dict()
    file = request.files.get("file")
    thumbnail = request.files.get("thumbnail")
    doc = doc_service.create_document(data, file, thumbnail, get_jwt_identity())
    return jsonify(doc), 201


def update_document(doc_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    file = request.files.get("file")
    thumbnail = request.files.get("thumbnail")
    doc = doc_service.update_document(doc_id, data, file, thumbnail)
    return jsonify(doc), 200


def download_document(doc_id):
    doc = doc_service.increment_download(doc_id)
    return jsonify({"url": doc.get("file_url")}), 200


def delete_document(doc_id):
    doc_service.delete_document(doc_id)
    return jsonify({"message": "Đã xóa"}), 200
