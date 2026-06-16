from bson import ObjectId
from app.repositories.base_repository import BaseRepository


class QuizRepository(BaseRepository):
    collection_name = "quizzes"

    def find_by_class(self, class_id, skip=0, limit=20):
        return self.find_all({"class_id": ObjectId(class_id)}, skip, limit, sort=[("created_at", -1)])


class QuestionRepository(BaseRepository):
    collection_name = "questions"

    def find_by_quiz(self, quiz_id):
        items, _ = self.find_all({"quiz_id": ObjectId(quiz_id)}, 0, 500, sort=[("order", 1)])
        return items


class QuizResultRepository(BaseRepository):
    collection_name = "quiz_results"

    def find_by_quiz(self, quiz_id, skip=0, limit=100):
        return self.find_all(
            {"quiz_id": ObjectId(quiz_id)}, skip, limit, sort=[("score", -1)]
        )

    def find_by_student_quiz(self, student_id, quiz_id):
        return self.collection.find_one({
            "student_id": ObjectId(student_id),
            "quiz_id": ObjectId(quiz_id),
        })
