from app.repositories.base_repository import BaseRepository


class AdminRepository(BaseRepository):
    collection_name = "admins"


class TeacherRepository(BaseRepository):
    collection_name = "teachers"

    def find_by_email(self, email):
        return self.collection.find_one({"email": email.lower()})


class StudentRepository(BaseRepository):
    collection_name = "students"

    def find_by_email(self, email):
        return self.collection.find_one({"email": email.lower()})

    def find_by_class(self, class_id, skip=0, limit=50):
        filter_q = {"class_ids": class_id}
        return self.find_all(filter_q, skip, limit)
