from flask import request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity
from app.services.quiz_service import QuizService

quiz_service = QuizService()


def list_quizzes():
    page = request.args.get("page", 1)
    class_id = request.args.get("class_id")
    return jsonify(quiz_service.list_quizzes(class_id, int(page))), 200


def get_quiz(quiz_id):
    include_answers = request.args.get("include_answers") == "true"
    quiz = quiz_service.get_quiz(quiz_id, include_answers)
    if not quiz:
        return jsonify({"message": "Không tìm thấy bài tập"}), 404
    return jsonify(quiz), 200


def create_quiz():
    data = request.get_json() or {}
    if not data.get("title") or not data.get("class_id"):
        return jsonify({"message": "Tiêu đề và lớp là bắt buộc"}), 400
    quiz, error = quiz_service.create_quiz(data, get_jwt_identity())
    if error:
        return jsonify({"message": error}), 400
    return jsonify(quiz), 201


def update_quiz(quiz_id):
    data = request.get_json() or {}
    if not data.get("title") or not data.get("class_id"):
        return jsonify({"message": "Tiêu đề và lớp là bắt buộc"}), 400
    quiz, error = quiz_service.update_quiz(quiz_id, data)
    if error:
        return jsonify({"message": error}), 400
    if not quiz:
        return jsonify({"message": "Không tìm thấy bài tập"}), 404
    return jsonify(quiz), 200


def add_question(quiz_id):
    data = request.get_json() or {}
    question = quiz_service.add_question(quiz_id, data)
    return jsonify(question), 201


def update_question(question_id):
    data = request.get_json() or {}
    question = quiz_service.update_question(question_id, data)
    return jsonify(question), 200


def delete_question(question_id):
    quiz_service.delete_question(question_id)
    return jsonify({"message": "Đã xóa"}), 200


def publish_quiz(quiz_id):
    quiz = quiz_service.publish_quiz(quiz_id)
    return jsonify(quiz), 200


def submit_quiz(quiz_id):
    data = request.get_json() or {}
    result, error = quiz_service.submit_quiz(
        quiz_id, get_jwt_identity(), data.get("answers", {}), data.get("time_taken", 0)
    )
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 201


def get_results(quiz_id):
    page = request.args.get("page", 1)
    return jsonify(quiz_service.get_results(quiz_id, int(page))), 200


def get_my_result(quiz_id):
    result = quiz_service.get_student_result(quiz_id, get_jwt_identity())
    if not result:
        return jsonify({"message": "Chưa có kết quả"}), 404
    return jsonify(result), 200


def export_results(quiz_id):
    output = quiz_service.export_results(quiz_id)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="ket_qua_bai_tap.xlsx",
    )


def delete_quiz(quiz_id):
    quiz_service.delete_quiz(quiz_id)
    return jsonify({"message": "Đã xóa"}), 200
