from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import video_controller as ctrl
from app.middleware.rbac import teacher_required

bp = Blueprint("video_tree", __name__, url_prefix="/api/video-tree")


@bp.route("/levels", methods=["GET"])
@jwt_required()
def list_levels():
    return ctrl.list_levels()


@bp.route("/levels/<int:level>/stories", methods=["GET"])
@jwt_required()
def list_stories(level):
    return ctrl.list_stories(level)


@bp.route("/stories/<story_id>/episodes", methods=["GET"])
@jwt_required()
def list_episodes(story_id):
    return ctrl.list_episodes(story_id)


@bp.route("/stories", methods=["POST"])
@jwt_required()
@teacher_required
def create_story():
    return ctrl.create_story()


@bp.route("/stories/<story_id>", methods=["PUT"])
@jwt_required()
@teacher_required
def update_story(story_id):
    return ctrl.update_story(story_id)


@bp.route("/stories/<story_id>", methods=["DELETE"])
@jwt_required()
@teacher_required
def delete_story(story_id):
    return ctrl.delete_story(story_id)
