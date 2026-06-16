from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import video_controller as ctrl
from app.middleware.rbac import teacher_required, student_required

bp = Blueprint("video_lessons", __name__, url_prefix="/api/video-lessons")


@bp.route("", methods=["GET"])
@jwt_required()
def list_lessons():
    return ctrl.list_lessons()


@bp.route("/<lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    return ctrl.get_lesson(lesson_id)


@bp.route("", methods=["POST"])
@jwt_required()
@teacher_required
def create_lesson():
    return ctrl.create_lesson()


@bp.route("/<lesson_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_lesson(lesson_id):
    return ctrl.update_lesson(lesson_id)


@bp.route("/<lesson_id>/subtitles", methods=["POST"])
@jwt_required()
@teacher_required
def add_subtitle(lesson_id):
    return ctrl.add_subtitle(lesson_id)


@bp.route("/<lesson_id>/subtitles/bulk", methods=["PUT"])
@jwt_required()
@teacher_required
def bulk_subtitles(lesson_id):
    return ctrl.bulk_subtitles(lesson_id)


@bp.route("/subtitles/<subtitle_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_subtitle(subtitle_id):
    return ctrl.update_subtitle(subtitle_id)


@bp.route("/subtitles/<subtitle_id>", methods=["DELETE"])
@jwt_required()
@teacher_required
def delete_subtitle(subtitle_id):
    return ctrl.delete_subtitle(subtitle_id)


@bp.route("/<lesson_id>/quiz-questions", methods=["POST"])
@jwt_required()
@teacher_required
def add_quiz_question(lesson_id):
    return ctrl.add_quiz_question(lesson_id)


@bp.route("/<lesson_id>/audio", methods=["POST"])
@jwt_required()
@student_required
def save_audio(lesson_id):
    return ctrl.save_audio(lesson_id)


@bp.route("/<lesson_id>/progress", methods=["GET"])
@jwt_required()
@student_required
def get_progress(lesson_id):
    return ctrl.get_progress(lesson_id)


@bp.route("/<lesson_id>/progress", methods=["POST"])
@jwt_required()
@student_required
def complete_step(lesson_id):
    return ctrl.complete_step(lesson_id)


@bp.route("/<lesson_id>/quiz-submit", methods=["POST"])
@jwt_required()
@student_required
def submit_video_quiz(lesson_id):
    return ctrl.submit_video_quiz(lesson_id)


@bp.route("/<lesson_id>", methods=["DELETE"])
@jwt_required()
@teacher_required
def delete_lesson(lesson_id):
    return ctrl.delete_lesson(lesson_id)
