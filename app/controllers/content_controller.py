from flask import request, jsonify
from app.services.content_service import ContentService

content_service = ContentService()


def homepage():
    return jsonify(content_service.get_homepage_data()), 200


def list_news():
    page = request.args.get("page", 1)
    published = request.args.get("all") != "true"
    return jsonify(content_service.list_news(int(page), 10, published)), 200


def get_news(slug_or_id):
    article = content_service.get_news(slug_or_id)
    if not article:
        return jsonify({"message": "Không tìm thấy bài viết"}), 404
    return jsonify(article), 200


def create_news():
    data = request.form.to_dict()
    image = request.files.get("image")
    article = content_service.create_news(data, image)
    return jsonify(article), 201


def update_news(article_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    image = request.files.get("image")
    article = content_service.update_news(article_id, data, image)
    return jsonify(article), 200


def delete_news(article_id):
    content_service.delete_news(article_id)
    return jsonify({"message": "Đã xóa"}), 200


def list_courses():
    page = request.args.get("page", 1)
    return jsonify(content_service.list_courses(int(page))), 200


def get_course(course_id):
    course = content_service.get_course(course_id)
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học"}), 404
    return jsonify(course), 200


def create_course():
    data = request.form.to_dict()
    image = request.files.get("image")
    course = content_service.create_course(data, image)
    return jsonify(course), 201


def update_course(course_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    image = request.files.get("image")
    course = content_service.update_course(course_id, data, image)
    return jsonify(course), 200


def delete_course(course_id):
    content_service.delete_course(course_id)
    return jsonify({"message": "Đã xóa"}), 200


def submit_contact():
    data = request.get_json() or {}
    try:
        contact = content_service.submit_contact(data)
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    return jsonify({"message": "Gửi liên hệ thành công", "contact": contact}), 201


def list_contacts():
    page = request.args.get("page", 1)
    status = request.args.get("status") or None
    return jsonify(content_service.list_contacts(int(page), 20, status)), 200


def get_contact(contact_id):
    contact = content_service.get_contact(contact_id)
    if not contact:
        return jsonify({"message": "Không tìm thấy liên hệ"}), 404
    return jsonify(contact), 200


def update_contact_status(contact_id):
    data = request.get_json() or {}
    status = data.get("status")
    if not status:
        return jsonify({"message": "Thiếu trạng thái"}), 400
    try:
        contact = content_service.update_contact_status(contact_id, status)
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    if not contact:
        return jsonify({"message": "Không tìm thấy liên hệ"}), 404
    return jsonify(contact), 200


def delete_contact(contact_id):
    if not content_service.delete_contact(contact_id):
        return jsonify({"message": "Không tìm thấy liên hệ"}), 404
    return jsonify({"message": "Đã xóa"}), 200


def get_seo(page_key):
    seo = content_service.get_seo(page_key)
    return jsonify(seo or {}), 200


def list_seo():
    return jsonify(content_service.list_seo()), 200


def update_seo(page_key):
    data = request.get_json() or {}
    seo = content_service.update_seo(page_key, data)
    return jsonify(seo), 200
