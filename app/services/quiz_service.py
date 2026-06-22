from datetime import datetime, timezone
from bson import ObjectId
from app.repositories.quiz_repository import QuizRepository, QuestionRepository, QuizResultRepository
from app.repositories.user_repository import StudentRepository
from app.utils.helpers import serialize_doc, utcnow, ensure_utc


class QuizService:
    def __init__(self):
        self.quiz_repo = QuizRepository()
        self.question_repo = QuestionRepository()
        self.result_repo = QuizResultRepository()
        self.student_repo = StudentRepository()

    def list_quizzes(self, class_id=None, page=1, per_page=20):
        skip = (page - 1) * per_page
        if class_id:
            items, total = self.quiz_repo.find_by_class(class_id, skip, per_page)
        else:
            items, total = self.quiz_repo.find_all({}, skip, per_page, sort=[("created_at", -1)])
        return {
            "items": [serialize_doc(q) for q in items],
            "pagination": {"page": page, "per_page": per_page, "total": total},
        }

    def get_quiz(self, quiz_id, include_answers=False):
        quiz = self.quiz_repo.find_by_id(quiz_id)
        if not quiz:
            return None
        questions = self.question_repo.find_by_quiz(quiz_id)
        if not include_answers:
            for q in questions:
                q.pop("correct_answer", None)
        quiz["questions"] = serialize_doc(questions)
        return serialize_doc(quiz)

    def _validate_question_data(self, data, index):
        if not data.get("content", "").strip():
            return f"Câu {index}: vui lòng nhập nội dung"
        options = data.get("options") or {}
        for key in ("A", "B", "C", "D"):
            if not str(options.get(key, "")).strip():
                return f"Câu {index}: vui lòng nhập đầy đủ đáp án {key}"
        if data.get("correct_answer") not in ("A", "B", "C", "D"):
            return f"Câu {index}: vui lòng chọn đáp án đúng"
        return None

    def create_quiz(self, data, teacher_id):
        questions_data = data.get("questions") or []
        for i, q in enumerate(questions_data, start=1):
            error = self._validate_question_data(q, i)
            if error:
                return None, error

        quiz_data = {
            "title": data["title"],
            "description": data.get("description", ""),
            "class_id": ObjectId(data["class_id"]),
            "teacher_id": ObjectId(teacher_id),
            "duration_minutes": int(data.get("duration_minutes", 30)),
            "open_at": data.get("open_at"),
            "close_at": data.get("close_at"),
            "type": data.get("type", "multiple_choice"),
            "status": "draft",
        }
        quiz = self.quiz_repo.create(quiz_data)
        quiz_id = str(quiz["_id"])
        created_questions = []
        for q in questions_data:
            question = self.add_question(quiz_id, q)
            created_questions.append(question)

        result = serialize_doc(quiz)
        if created_questions:
            result["questions"] = created_questions
        return result, None

    def update_quiz(self, quiz_id, data):
        quiz = self.quiz_repo.find_by_id(quiz_id)
        if not quiz:
            return None, "Không tìm thấy bài tập"

        questions_data = data.get("questions")
        if questions_data is not None:
            if len(questions_data) == 0:
                return None, "Vui lòng thêm ít nhất một câu hỏi"
            for i, q in enumerate(questions_data, start=1):
                error = self._validate_question_data(q, i)
                if error:
                    return None, error

        update_data = {}
        if data.get("title"):
            update_data["title"] = data["title"]
        if data.get("description") is not None:
            update_data["description"] = data["description"]
        if data.get("class_id"):
            update_data["class_id"] = ObjectId(data["class_id"])
        if data.get("duration_minutes") is not None:
            update_data["duration_minutes"] = int(data["duration_minutes"])

        if update_data:
            self.quiz_repo.update(quiz_id, update_data)

        if questions_data is not None:
            self.question_repo.collection.delete_many({"quiz_id": ObjectId(quiz_id)})
            for q in questions_data:
                self.add_question(quiz_id, q)

        return self.get_quiz(quiz_id, include_answers=True), None

    def add_question(self, quiz_id, data):
        questions = self.question_repo.find_by_quiz(quiz_id)
        q_type = data.get("question_type", "multiple_choice")
        q_data = {
            "quiz_id": ObjectId(quiz_id),
            "content": data["content"],
            "image": data.get("image", ""),
            "question_type": q_type,
            "order": len(questions) + 1,
        }
        if q_type == "short_answer":
            q_data["options"] = {}
            q_data["correct_answer"] = data.get("sample_answer", data.get("correct_answer", ""))
        else:
            q_data["options"] = data["options"]
            q_data["correct_answer"] = data["correct_answer"]
        question = self.question_repo.create(q_data)
        return serialize_doc(question)

    def update_question(self, question_id, data):
        allowed = {"content", "image", "options", "correct_answer", "order"}
        update_data = {k: v for k, v in data.items() if k in allowed}
        q = self.question_repo.update(question_id, update_data)
        return serialize_doc(q)

    def delete_question(self, question_id):
        return self.question_repo.delete(question_id)

    def publish_quiz(self, quiz_id):
        quiz = self.quiz_repo.update(quiz_id, {"status": "published"})
        return serialize_doc(quiz)

    def submit_quiz(self, quiz_id, student_id, answers, time_taken=0):
        existing = self.result_repo.find_by_student_quiz(student_id, quiz_id)
        if existing:
            return None, "Bạn đã nộp bài rồi"

        quiz = self.quiz_repo.find_by_id(quiz_id)
        if not quiz:
            return None, "Bài tập không tồn tại"

        now = utcnow()
        open_at = ensure_utc(quiz.get("open_at"))
        close_at = ensure_utc(quiz.get("close_at"))
        if open_at and now < open_at:
            return None, "Bài tập chưa mở"
        if close_at and now > close_at:
            return None, "Bài tập đã đóng"

        questions = self.question_repo.find_by_quiz(quiz_id)
        correct = 0
        wrong = 0
        pending = 0
        gradable_total = 0
        detail = []
        for q in questions:
            qid = str(q["_id"])
            student_ans = answers.get(qid, "")
            q_type = q.get("question_type", "multiple_choice")
            if q_type == "short_answer":
                sample = (q.get("correct_answer") or "").strip().lower()
                text = (student_ans or "").strip()
                is_correct = bool(sample and text.lower() == sample)
                needs_review = not sample or not is_correct
                if needs_review:
                    pending += 1
                else:
                    correct += 1
                    gradable_total += 1
                detail.append({
                    "question_id": qid,
                    "content": q.get("content"),
                    "student_answer": student_ans,
                    "correct_answer": q.get("correct_answer"),
                    "is_correct": is_correct if not needs_review else None,
                    "question_type": q_type,
                    "needs_review": needs_review,
                })
            else:
                gradable_total += 1
                is_correct = student_ans == q.get("correct_answer")
                if is_correct:
                    correct += 1
                else:
                    wrong += 1
                detail.append({
                    "question_id": qid,
                    "content": q.get("content"),
                    "student_answer": student_ans,
                    "correct_answer": q.get("correct_answer"),
                    "is_correct": is_correct,
                    "question_type": q_type,
                })

        total = len(questions)
        score = round((correct / gradable_total) * 10, 1) if gradable_total else 0

        student = self.student_repo.find_by_id(student_id)
        result_data = {
            "quiz_id": ObjectId(quiz_id),
            "student_id": ObjectId(student_id),
            "student_name": student.get("full_name", "") if student else "",
            "email": student.get("email", "") if student else "",
            "score": score,
            "correct": correct,
            "wrong": wrong,
            "pending_review": pending,
            "total": total,
            "time_taken": time_taken,
            "answers_detail": detail,
            "submitted_at": now,
        }
        result = self.result_repo.create(result_data)
        return serialize_doc(result), None

    def get_results(self, quiz_id, page=1, per_page=50):
        skip = (page - 1) * per_page
        items, total = self.result_repo.find_by_quiz(quiz_id, skip, per_page)
        return {
            "items": serialize_doc(items),
            "pagination": {"page": page, "per_page": per_page, "total": total},
            "stats": {
                "avg_score": round(sum(r.get("score", 0) for r in items) / len(items), 1) if items else 0,
                "top_score": max((r.get("score", 0) for r in items), default=0),
            },
        }

    def get_student_result(self, quiz_id, student_id):
        result = self.result_repo.find_by_student_quiz(student_id, quiz_id)
        return serialize_doc(result)

    def export_results(self, quiz_id):
        items, _ = self.result_repo.find_by_quiz(quiz_id, 0, 1000)
        quiz = self.quiz_repo.find_by_id(quiz_id)
        from app.utils.excel_export import export_quiz_results
        data = []
        for r in items:
            data.append({
                "student_name": r.get("student_name"),
                "email": r.get("email"),
                "score": r.get("score"),
                "correct": r.get("correct"),
                "wrong": r.get("wrong"),
                "time_taken": r.get("time_taken"),
                "submitted_at": r.get("submitted_at", "").isoformat() if r.get("submitted_at") else "",
            })
        return export_quiz_results(data, quiz.get("title", "") if quiz else "")

    def delete_quiz(self, quiz_id):
        self.question_repo.collection.delete_many({"quiz_id": ObjectId(quiz_id)})
        self.result_repo.collection.delete_many({"quiz_id": ObjectId(quiz_id)})
        return self.quiz_repo.delete(quiz_id)
