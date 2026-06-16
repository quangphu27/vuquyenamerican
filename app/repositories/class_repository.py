from bson import ObjectId
from app.repositories.base_repository import BaseRepository


class ClassRepository(BaseRepository):
    collection_name = "classes"

    def find_by_teacher(self, teacher_id, skip=0, limit=50):
        return self.find_all({"teacher_id": ObjectId(teacher_id)}, skip, limit)

    def add_student(self, class_id, student_id):
        self.collection.update_one(
            {"_id": ObjectId(class_id)},
            {"$addToSet": {"student_ids": ObjectId(student_id)}},
        )

    def remove_student(self, class_id, student_id):
        self.collection.update_one(
            {"_id": ObjectId(class_id)},
            {"$pull": {"student_ids": ObjectId(student_id)}},
        )
