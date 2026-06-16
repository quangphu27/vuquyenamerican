from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.video_service import VideoService

video_service = VideoService()


def list_lessons():
    page = request.args.get("page", 1)
    class_id = request.args.get("class_id")
    return jsonify(video_service.list_lessons(class_id, int(page))), 200


def get_lesson(lesson_id):
    include_quiz = request.args.get("include_quiz") == "true"
    lesson = video_service.get_lesson(lesson_id, include_quiz)
    if not lesson:
        return jsonify({"message": "Không tìm thấy bài học"}), 404
    return jsonify(lesson), 200


def create_lesson():
    data = request.form.to_dict()
    video_audio = request.files.get("video_with_audio")
    video_muted = request.files.get("video_muted")
    lesson = video_service.create_lesson(data, get_jwt_identity(), video_audio, video_muted)
    return jsonify(lesson), 201


def update_lesson(lesson_id):
    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form.to_dict()
        video_audio = request.files.get("video_with_audio")
        video_muted = request.files.get("video_muted")
    else:
        data = request.get_json() or {}
        video_audio = None
        video_muted = None
    lesson = video_service.update_lesson(lesson_id, data, video_audio, video_muted)
    if not lesson:
        return jsonify({"message": "Không tìm thấy bài học"}), 404
    return jsonify(lesson), 200


def add_subtitle(lesson_id):
    data = request.get_json() or {}
    sub = video_service.add_subtitle(lesson_id, data)
    return jsonify(sub), 201


def update_subtitle(subtitle_id):
    data = request.get_json() or {}
    sub = video_service.update_subtitle(subtitle_id, data)
    return jsonify(sub), 200


def delete_subtitle(subtitle_id):
    video_service.delete_subtitle(subtitle_id)
    return jsonify({"message": "Đã xóa"}), 200


def bulk_subtitles(lesson_id):
    data = request.get_json() or {}
    subs = video_service.bulk_save_subtitles(lesson_id, data.get("subtitles", []))
    return jsonify(subs), 200


def add_quiz_question(lesson_id):
    data = request.get_json() or {}
    q = video_service.add_video_quiz_question(lesson_id, data)
    return jsonify(q), 201


def save_audio(lesson_id):
    ok, error = video_service.can_access_step(get_jwt_identity(), lesson_id, "dub")
    if not ok:
        return jsonify({"message": error}), 403
    audio = request.files.get("audio")
    if not audio:
        return jsonify({"message": "File âm thanh bắt buộc"}), 400
    result, error = video_service.save_audio_record(get_jwt_identity(), lesson_id, audio)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(result), 201


def submit_video_quiz(lesson_id):
    data = request.get_json() or {}
    ok, error = video_service.can_access_step(get_jwt_identity(), lesson_id, "quiz")
    if not ok:
        return jsonify({"message": error}), 403
    result = video_service.submit_video_quiz(lesson_id, get_jwt_identity(), data.get("answers", {}))
    return jsonify(result), 200


def get_progress(lesson_id):
    progress = video_service.get_progress(get_jwt_identity(), lesson_id)
    return jsonify(progress), 200


def complete_step(lesson_id):
    data = request.get_json() or {}
    step = data.get("step")
    progress, error = video_service.complete_step(get_jwt_identity(), lesson_id, step)
    if error:
        status = 403 if "hoàn thành" in error.lower() or "bước" in error.lower() else 400
        return jsonify({"message": error}), status
    return jsonify(progress), 200


def delete_lesson(lesson_id):
    video_service.delete_lesson(lesson_id)
    return jsonify({"message": "Đã xóa"}), 200
