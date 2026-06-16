from bson import ObjectId
from app.extensions import get_db
from app.repositories.class_repository import ClassRepository
from app.repositories.quiz_repository import QuizRepository, QuizResultRepository
from app.repositories.video_repository import VideoLessonRepository
from app.utils.helpers import serialize_doc, utcnow
from datetime import timedelta


class DashboardService:
    @property
    def db(self):
        return get_db()

    def admin_stats(self):
        return {
            "students": self.db.students.count_documents({"status": "approved"}),
            "teachers": self.db.teachers.count_documents({}),
            "classes": self.db.classes.count_documents({}),
            "quizzes": self.db.quizzes.count_documents({}),
            "documents": self.db.documents.count_documents({}),
            "video_lessons": self.db.video_lessons.count_documents({}),
            "pending_students": self.db.students.count_documents({"status": "pending"}),
        }

    def admin_recent_activity(self):
        activities = []
        for collection, label in [
            ("students", "Học sinh mới đăng ký"),
            ("quiz_results", "Bài tập được nộp"),
            ("documents", "Tài liệu mới"),
            ("news", "Tin tức mới"),
        ]:
            items = list(self.db[collection].find().sort("created_at", -1).limit(3))
            for item in items:
                activities.append({
                    "type": collection,
                    "label": label,
                    "name": item.get("full_name") or item.get("title") or item.get("student_name", ""),
                    "created_at": item.get("created_at"),
                })
        activities.sort(key=lambda x: x.get("created_at") or utcnow(), reverse=True)
        return serialize_doc(activities[:10])

    def admin_top_classes(self):
        classes = list(self.db.classes.find().limit(20))
        result = []
        for cls in classes:
            result.append({
                "id": str(cls["_id"]),
                "name": cls.get("name"),
                "student_count": len(cls.get("student_ids", [])),
            })
        result.sort(key=lambda x: x["student_count"], reverse=True)
        return result[:5]

    def teacher_stats(self, teacher_id):
        class_repo = ClassRepository()
        classes, _ = class_repo.find_by_teacher(teacher_id, 0, 100)
        class_ids = [c["_id"] for c in classes]
        student_count = sum(len(c.get("student_ids", [])) for c in classes)
        quiz_count = self.db.quizzes.count_documents({"teacher_id": ObjectId(teacher_id)})
        return {
            "class_count": len(classes),
            "student_count": student_count,
            "quiz_count": quiz_count,
            "video_count": self.db.video_lessons.count_documents({"teacher_id": ObjectId(teacher_id)}),
        }

    def teacher_assignments(self, teacher_id):
        quizzes, _ = QuizRepository().find_all(
            {"teacher_id": ObjectId(teacher_id)}, 0, 10, sort=[("created_at", -1)]
        )
        return serialize_doc(quizzes)

    def student_stats(self, student_id):
        results = list(self.db.quiz_results.find({"student_id": ObjectId(student_id)}))
        avg_score = round(sum(r.get("score", 0) for r in results) / len(results), 1) if results else 0
        student = self.db.students.find_one({"_id": ObjectId(student_id)})
        return {
            "avg_score": avg_score,
            "completed_quizzes": len(results),
            "class_count": len(student.get("class_ids", [])) if student else 0,
        }

    def student_recent_quizzes(self, student_id):
        class_ids = []
        student = self.db.students.find_one({"_id": ObjectId(student_id)})
        if student:
            class_ids = student.get("class_ids", [])

        quizzes = list(self.db.quizzes.find({
            "class_id": {"$in": class_ids},
            "status": "published",
        }).sort("created_at", -1).limit(5))

        result = []
        for q in quizzes:
            submitted = self.db.quiz_results.find_one({
                "quiz_id": q["_id"],
                "student_id": ObjectId(student_id),
            })
            result.append({
                **serialize_doc(q),
                "submitted": submitted is not None,
                "score": submitted.get("score") if submitted else None,
            })
        return result
