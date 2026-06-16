from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import AdminRepository, TeacherRepository, StudentRepository
from app.models.user_model import UserModel


class AuthService:
    def __init__(self):
        self.admin_repo = AdminRepository()
        self.teacher_repo = TeacherRepository()
        self.student_repo = StudentRepository()

    def _get_repo_by_role(self, role):
        return {
            "admin": self.admin_repo,
            "teacher": self.teacher_repo,
            "student": self.student_repo,
        }.get(role)

    def _find_user(self, email):
        email = email.lower().strip()
        for repo in (self.admin_repo, self.teacher_repo, self.student_repo):
            user = repo.collection.find_one({"email": email})
            if user:
                role = "admin" if repo.collection_name == "admins" else (
                    "teacher" if repo.collection_name == "teachers" else "student"
                )
                user["role"] = role
                return user
        return None

    def _get_status_error(self, status):
        messages = {
            "pending": "Tài khoản chưa được duyệt. Vui lòng chờ admin phê duyệt.",
            "rejected": "Tài khoản đã bị từ chối",
            "inactive": "Tài khoản đã bị khóa",
        }
        return messages.get(status)

    def validate_session_user(self, user_id, role):
        if role == "admin":
            return None
        repo = self._get_repo_by_role(role)
        if not repo:
            return "Không tìm thấy người dùng"
        user = repo.find_by_id(user_id)
        if not user:
            return "Không tìm thấy người dùng"
        return self._get_status_error(user.get("status", "approved"))

    def login(self, email, password):
        user = self._find_user(email)
        if not user:
            return None, "Email hoặc mật khẩu không đúng"
        if not UserModel.check_password(password, user["password"]):
            return None, "Email hoặc mật khẩu không đúng"
        status_error = self._get_status_error(user.get("status", "approved"))
        if status_error:
            return None, status_error

        identity = str(user["_id"])
        additional = {"role": user["role"], "email": user["email"]}
        return {
            "access_token": create_access_token(identity=identity, additional_claims=additional),
            "refresh_token": create_refresh_token(identity=identity, additional_claims=additional),
            "user": UserModel.to_public(user),
        }, None

    def register_student(self, data):
        email = data["email"].lower().strip()
        if self._find_user(email):
            return None, "Email đã tồn tại"

        student_data = {
            "email": email,
            "password": UserModel.hash_password(data["password"]),
            "full_name": data["full_name"],
            "phone": data.get("phone", ""),
            "role": "student",
            "status": "pending",
            "class_ids": [],
            "avatar": None,
        }
        student = self.student_repo.create(student_data)
        return UserModel.to_public(student), None

    def refresh(self, user_id, claims):
        role = claims.get("role")
        status_error = self.validate_session_user(user_id, role)
        if status_error:
            return None, status_error
        additional = {"role": role, "email": claims.get("email")}
        return create_access_token(identity=user_id, additional_claims=additional), None

    def get_user_by_id(self, user_id, role):
        repo = self._get_repo_by_role(role)
        if not repo:
            return None
        user = repo.find_by_id(user_id)
        if user:
            user["role"] = role
        return UserModel.to_public(user)

    def update_profile(self, user_id, role, data):
        repo = self._get_repo_by_role(role)
        if not repo:
            return None, "Không tìm thấy người dùng"

        allowed = {"full_name", "phone", "avatar"}
        if role == "teacher":
            allowed.add("specialization")

        update_data = {}
        if "full_name" in data and data["full_name"]:
            update_data["full_name"] = data["full_name"].strip()
        if "phone" in data:
            update_data["phone"] = data["phone"].strip()
        if "avatar" in data:
            update_data["avatar"] = data["avatar"]
        if role == "teacher" and "specialization" in data:
            update_data["specialization"] = data["specialization"].strip()

        if not update_data:
            user = repo.find_by_id(user_id)
            if user:
                user["role"] = role
            return UserModel.to_public(user), None

        updated = repo.update(user_id, update_data)
        if not updated:
            return None, "Không tìm thấy người dùng"
        updated["role"] = role
        return UserModel.to_public(updated), None

    def change_password(self, user_id, role, current_password, new_password):
        if not current_password or not new_password:
            return None, "Mật khẩu hiện tại và mật khẩu mới là bắt buộc"
        if len(new_password) < 6:
            return None, "Mật khẩu mới tối thiểu 6 ký tự"

        repo = self._get_repo_by_role(role)
        if not repo:
            return None, "Không tìm thấy người dùng"

        user = repo.find_by_id(user_id)
        if not user:
            return None, "Không tìm thấy người dùng"
        if not UserModel.check_password(current_password, user["password"]):
            return None, "Mật khẩu hiện tại không đúng"

        updated = repo.update(user_id, {"password": UserModel.hash_password(new_password)})
        if not updated:
            return None, "Không thể cập nhật mật khẩu"
        updated["role"] = role
        return UserModel.to_public(updated), None
