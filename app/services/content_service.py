import re
from app.repositories.content_repository import NewsRepository, SeoRepository, CourseRepository, ContactRepository
from app.utils.helpers import serialize_doc, paginate
from app.utils.cloudinary_util import upload_file
from flask_mail import Message
from app.extensions import mail
from flask import current_app


class ContentService:
    def __init__(self):
        self.news_repo = NewsRepository()
        self.seo_repo = SeoRepository()
        self.course_repo = CourseRepository()
        self.contact_repo = ContactRepository()

    def _slugify(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text

    # News
    def list_news(self, page=1, per_page=10, published_only=True):
        def query(skip, limit):
            if published_only:
                return self.news_repo.find_published(skip, limit)
            return self.news_repo.find_all({}, skip, limit, sort=[("created_at", -1)])

        return paginate(query, page, per_page)

    def get_news(self, slug_or_id):
        if len(slug_or_id) == 24:
            article = self.news_repo.find_by_id(slug_or_id)
        else:
            article = self.news_repo.find_by_slug(slug_or_id)
        return serialize_doc(article)

    def create_news(self, data, image=None):
        img = upload_file(image, subfolder="news") if image else None
        article_data = {
            "title": data["title"],
            "slug": self._slugify(data.get("slug") or data["title"]),
            "excerpt": data.get("excerpt", ""),
            "content": data.get("content", ""),
            "thumbnail": img["url"] if img else data.get("thumbnail", ""),
            "status": data.get("status", "draft"),
            "seo_title": data.get("seo_title", data["title"]),
            "seo_description": data.get("seo_description", ""),
            "published_at": data.get("published_at"),
        }
        article = self.news_repo.create(article_data)
        return serialize_doc(article)

    def update_news(self, article_id, data, image=None):
        update_data = {k: data[k] for k in ("title", "excerpt", "content", "status", "seo_title", "seo_description") if k in data}
        if "title" in data:
            update_data["slug"] = self._slugify(data.get("slug") or data["title"])
        if image:
            img = upload_file(image, subfolder="news")
            if img:
                update_data["thumbnail"] = img["url"]
        article = self.news_repo.update(article_id, update_data)
        return serialize_doc(article)

    def delete_news(self, article_id):
        return self.news_repo.delete(article_id)

    # SEO
    def get_seo(self, page_key):
        seo = self.seo_repo.find_by_page(page_key)
        return serialize_doc(seo)

    def list_seo(self):
        items, _ = self.seo_repo.find_all({}, 0, 100)
        return serialize_doc(items)

    def update_seo(self, page_key, data):
        seo = self.seo_repo.upsert_page(page_key, data)
        return serialize_doc(seo)

    # Courses
    def list_courses(self, page=1, per_page=20):
        def query(skip, limit):
            return self.course_repo.find_active(skip, limit)
        return paginate(query, page, per_page)

    def get_course(self, course_id):
        return serialize_doc(self.course_repo.find_by_id(course_id))

    def create_course(self, data, image=None):
        img = upload_file(image, subfolder="courses") if image else None
        course_data = {
            "title": data["title"],
            "description": data.get("description", ""),
            "fee": data.get("fee", ""),
            "duration": data.get("duration", ""),
            "image": img["url"] if img else data.get("image", ""),
            "is_active": data.get("is_active", True),
            "order": int(data.get("order", 0)),
        }
        course = self.course_repo.create(course_data)
        return serialize_doc(course)

    def update_course(self, course_id, data, image=None):
        update_data = {k: data[k] for k in ("title", "description", "fee", "duration", "is_active", "order") if k in data}
        if image:
            img = upload_file(image, subfolder="courses")
            if img:
                update_data["image"] = img["url"]
        course = self.course_repo.update(course_id, update_data)
        return serialize_doc(course)

    def delete_course(self, course_id):
        return self.course_repo.delete(course_id)

    # Contact
    def submit_contact(self, data):
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        message = (data.get("message") or "").strip()
        if not name or not email or not message:
            raise ValueError("Vui lòng nhập đầy đủ họ tên, email và nội dung")
        contact = self.contact_repo.create({
            "name": name,
            "email": email,
            "phone": (data.get("phone") or "").strip(),
            "message": message,
            "status": "new",
        })
        try:
            admin_email = current_app.config.get("ADMIN_EMAIL")
            if admin_email:
                msg = Message(
                    subject=f"Liên hệ mới từ {data['name']}",
                    recipients=[admin_email],
                    body=f"Họ tên: {data['name']}\nEmail: {data['email']}\nĐiện thoại: {data.get('phone')}\n\n{data['message']}",
                )
                mail.send(msg)
        except Exception:
            pass
        return serialize_doc(contact)

    def list_contacts(self, page=1, per_page=20, status=None):
        filter_query = {}
        if status:
            filter_query["status"] = status

        def query(skip, limit):
            return self.contact_repo.find_all(
                filter_query, skip, limit, sort=[("created_at", -1)]
            )

        return paginate(query, page, per_page)

    def get_contact(self, contact_id):
        contact = self.contact_repo.find_by_id(contact_id)
        return serialize_doc(contact) if contact else None

    def update_contact_status(self, contact_id, status):
        allowed = {"new", "read", "replied"}
        if status not in allowed:
            raise ValueError("Trạng thái không hợp lệ")
        contact = self.contact_repo.find_by_id(contact_id)
        if not contact:
            return None
        updated = self.contact_repo.update(contact_id, {"status": status})
        return serialize_doc(updated)

    def delete_contact(self, contact_id):
        return self.contact_repo.delete(contact_id)

    def get_homepage_data(self):
        news_result = self.list_news(1, 6)
        courses_result = self.list_courses(1, 6)
        seo = self.get_seo("home")
        return {
            "news": news_result["items"],
            "courses": courses_result["items"],
            "seo": seo,
        }
