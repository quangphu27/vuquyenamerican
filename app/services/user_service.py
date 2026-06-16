from bson import ObjectId
from app.repositories.user_repository import TeacherRepository, StudentRepository
from app.models.user_model import UserModel


class UserService:
    ALLOWED_STATUS_TRANSITIONS = {
        ("pending", "approved"),
        ("pending", "rejected"),
        ("approved", "inactive"),
        ("inactive", "approved"),
        ("rejected", "approved"),
    }

    def __init__(self):
        self.teacher_repo = TeacherRepository()
        self.student_repo = StudentRepository()

    def list_teachers(self, page=1, per_page=20):
        from app.utils.helpers import paginate
        skip = (page - 1) * per_page
        items, total = self.teacher_repo.find_all({}, skip, per_page, sort=[("created_at", -1)])
        return {
            "items": [UserModel.to_public(t) for t in items],
            "pagination": {"page": page, "per_page": per_page, "total": total},
        }

    def list_students(self, status=None, page=1, per_page=20):
        skip = (page - 1) * per_page
        filter_q = {}
        if status:
            filter_q["status"] = status
        items, total = self.student_repo.find_all(filter_q, skip, per_page, sort=[("created_at", -1)])
        return {
            "items": [UserModel.to_public(s) for s in items],
            "pagination": {"page": page, "per_page": per_page, "total": total},
        }

    def create_teacher(self, data):
        email = data["email"].lower().strip()
        if self.teacher_repo.find_by_email(email) or self.student_repo.find_by_email(email):
            return None, "Email đã tồn tại"
        teacher_data = {
            "email": email,
            "password": UserModel.hash_password(data["password"]),
            "full_name": data["full_name"],
            "phone": data.get("phone", ""),
            "role": "teacher",
            "status": "approved",
            "specialization": data.get("specialization", ""),
            "avatar": data.get("avatar"),
        }
        teacher = self.teacher_repo.create(teacher_data)
        return UserModel.to_public(teacher), None

    def update_account_status(self, user_id, role, status):
        if role not in ("student", "teacher"):
            return None, "Không hỗ trợ cập nhật trạng thái cho vai trò này"
        if status not in UserModel.STATUSES:
            return None, "Trạng thái không hợp lệ"

        repo = self.teacher_repo if role == "teacher" else self.student_repo
        user = repo.find_by_id(user_id)
        if not user:
            return None, "Không tìm thấy người dùng"

        current_status = user.get("status", "approved")
        if current_status == status:
            user["role"] = role
            return UserModel.to_public(user), None

        if (current_status, status) not in self.ALLOWED_STATUS_TRANSITIONS:
            return None, "Không thể thực hiện thao tác này với trạng thái hiện tại"

        updated = repo.update(user_id, {"status": status})
        if updated:
            updated["role"] = role
        return UserModel.to_public(updated), None

    def update_student_status(self, student_id, status):
        return self.update_account_status(student_id, "student", status)

    def update_teacher_status(self, teacher_id, status):
        return self.update_account_status(teacher_id, "teacher", status)

    def update_user(self, user_id, role, data):
        repo = self.teacher_repo if role == "teacher" else self.student_repo
        allowed = {"full_name", "phone", "avatar", "specialization"}
        update_data = {k: v for k, v in data.items() if k in allowed and v is not None}
        if "password" in data and data["password"]:
            update_data["password"] = UserModel.hash_password(data["password"])
        user = repo.update(user_id, update_data)
        if user:
            user["role"] = role
        return UserModel.to_public(user), None

    def delete_user(self, user_id, role):
        repo = self.teacher_repo if role == "teacher" else self.student_repo
        return repo.delete(user_id)
