from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import quiz_controller as ctrl
from app.middleware.rbac import teacher_required, student_required

bp = Blueprint("quizzes", __name__, url_prefix="/api/quizzes")


@bp.route("", methods=["GET"])
@jwt_required()
def list_quizzes():
    return ctrl.list_quizzes()


@bp.route("/<quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    return ctrl.get_quiz(quiz_id)


@bp.route("", methods=["POST"])
@jwt_required()
@teacher_required
def create_quiz():
    return ctrl.create_quiz()


@bp.route("/<quiz_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_quiz(quiz_id):
    return ctrl.update_quiz(quiz_id)


@bp.route("/<quiz_id>/questions", methods=["POST"])
@jwt_required()
@teacher_required
def add_question(quiz_id):
    return ctrl.add_question(quiz_id)


@bp.route("/questions/<question_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_question(question_id):
    return ctrl.update_question(question_id)


@bp.route("/questions/<question_id>", methods=["DELETE"])
@jwt_required()
@teacher_required
def delete_question(question_id):
    return ctrl.delete_question(question_id)


@bp.route("/<quiz_id>/publish", methods=["POST"])
@jwt_required()
@teacher_required
def publish_quiz(quiz_id):
    return ctrl.publish_quiz(quiz_id)


@bp.route("/<quiz_id>/submit", methods=["POST"])
@jwt_required()
@student_required
def submit_quiz(quiz_id):
    return ctrl.submit_quiz(quiz_id)


@bp.route("/<quiz_id>/results", methods=["GET"])
@jwt_required()
@teacher_required
def get_results(quiz_id):
    return ctrl.get_results(quiz_id)


@bp.route("/<quiz_id>/my-result", methods=["GET"])
@jwt_required()
@student_required
def get_my_result(quiz_id):
    return ctrl.get_my_result(quiz_id)


@bp.route("/<quiz_id>/export", methods=["GET"])
@jwt_required()
@teacher_required
def export_results(quiz_id):
    return ctrl.export_results(quiz_id)


@bp.route("/<quiz_id>", methods=["DELETE"])
@jwt_required()
@teacher_required
def delete_quiz(quiz_id):
    return ctrl.delete_quiz(quiz_id)
