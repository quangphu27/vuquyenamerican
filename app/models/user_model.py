import bcrypt


class UserModel:
  ROLES = ("admin", "teacher", "student")
  STATUSES = ("pending", "approved", "rejected", "inactive")

  @staticmethod
  def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

  @staticmethod
  def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

  @staticmethod
  def to_public(doc):
    if not doc:
      return None
    return {
      "id": str(doc["_id"]),
      "email": doc.get("email"),
      "full_name": doc.get("full_name"),
      "role": doc.get("role"),
      "status": doc.get("status"),
      "phone": doc.get("phone"),
      "avatar": doc.get("avatar"),
      "specialization": doc.get("specialization"),
      "class_ids": [str(c) for c in doc.get("class_ids", [])],
      "created_at": doc.get("created_at"),
    }
