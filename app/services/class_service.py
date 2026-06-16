from bson import ObjectId
from app.repositories.class_repository import ClassRepository
from app.repositories.user_repository import StudentRepository, TeacherRepository
from app.utils.helpers import serialize_doc


class ClassService:
    def __init__(self):
        self.class_repo = ClassRepository()
        self.student_repo = StudentRepository()
        self.teacher_repo = TeacherRepository()

    def _enrich_class(self, cls):
        if not cls:
            return None
        teacher = self.teacher_repo.find_by_id(str(cls.get("teacher_id", "")))
        students = []
        for sid in cls.get("student_ids", []):
            s = self.student_repo.find_by_id(str(sid))
            if s:
                students.append({
                    "id": str(s["_id"]),
                    "full_name": s.get("full_name"),
                    "email": s.get("email"),
                    "status": s.get("status"),
                })
        return {
            **serialize_doc(cls),
            "teacher_name": teacher.get("full_name") if teacher else "",
            "students": students,
            "student_count": len(students),
        }

    def list_classes(self, teacher_id=None, page=1, per_page=20):
        skip = (page - 1) * per_page
        filter_q = {}
        if teacher_id:
            filter_q["teacher_id"] = ObjectId(teacher_id)
        items, total = self.class_repo.find_all(filter_q, skip, per_page, sort=[("created_at", -1)])
        return {
            "items": [self._enrich_class(c) for c in items],
            "pagination": {"page": page, "per_page": per_page, "total": total},
        }

    def get_class(self, class_id):
        cls = self.class_repo.find_by_id(class_id)
        return self._enrich_class(cls)

    def create_class(self, data, teacher_id=None):
        class_data = {
            "name": data["name"],
            "grade": data.get("grade", ""),
            "description": data.get("description", ""),
            "teacher_id": ObjectId(teacher_id or data["teacher_id"]),
            "student_ids": [],
        }
        cls = self.class_repo.create(class_data)
        return self._enrich_class(cls)

    def update_class(self, class_id, data):
        allowed = {"name", "grade", "description", "teacher_id"}
        update_data = {}
        for k, v in data.items():
            if k in allowed and v is not None:
                update_data[k] = ObjectId(v) if k in ("teacher_id",) else v
        cls = self.class_repo.update(class_id, update_data)
        return self._enrich_class(cls)

    def add_student(self, class_id, student_id):
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return None, "Học sinh không tồn tại"
        self.class_repo.add_student(class_id, student_id)
        self.student_repo.collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$addToSet": {"class_ids": ObjectId(class_id)}},
        )
        return self.get_class(class_id), None

    def remove_student(self, class_id, student_id):
        self.class_repo.remove_student(class_id, student_id)
        self.student_repo.collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$pull": {"class_ids": ObjectId(class_id)}},
        )
        return self.get_class(class_id), None

    def transfer_student(self, from_class_id, to_class_id, student_id):
        self.remove_student(from_class_id, student_id)
        return self.add_student(to_class_id, student_id)

    def delete_class(self, class_id):
        return self.class_repo.delete(class_id)
