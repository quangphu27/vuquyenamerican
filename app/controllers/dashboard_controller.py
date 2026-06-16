from flask import jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.services.dashboard_service import DashboardService

dashboard_service = DashboardService()


def admin_dashboard():
    return jsonify({
        "stats": dashboard_service.admin_stats(),
        "recent_activity": dashboard_service.admin_recent_activity(),
        "top_classes": dashboard_service.admin_top_classes(),
    }), 200


def teacher_dashboard():
    teacher_id = get_jwt_identity()
    return jsonify({
        "stats": dashboard_service.teacher_stats(teacher_id),
        "assignments": dashboard_service.teacher_assignments(teacher_id),
    }), 200


def student_dashboard():
    student_id = get_jwt_identity()
    return jsonify({
        "stats": dashboard_service.student_stats(student_id),
        "recent_quizzes": dashboard_service.student_recent_quizzes(student_id),
    }), 200
