"""Seed sample data for Vu Quyen American."""
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import get_db
from app.models.user_model import UserModel


def seed():
    app = create_app()
    with app.app_context():
        db = get_db()
        if db.admins.count_documents({}) > 0:
            print("Database already seeded. Skipping.")
            return

        now = datetime.now(timezone.utc)

        db.admins.insert_one({
            "email": "admin@vuquyenamerican.com",
            "password": UserModel.hash_password("admin123"),
            "full_name": "Admin Vu Quyen",
            "role": "admin",
            "status": "approved",
            "phone": "0901234567",
            "created_at": now,
            "updated_at": now,
        })

        teacher_result = db.teachers.insert_one({
            "email": "vuquyen101982@gmail.com",
            "password": UserModel.hash_password("teacher123"),
            "full_name": "Vu Thi Quyen",
            "role": "teacher",
            "status": "approved",
            "phone": "0388019858",
            "specialization": "Tieng Anh - TTNN American",
            "workplace": "TTNN American",
            "created_at": now,
            "updated_at": now,
        })
        teacher_id = teacher_result.inserted_id

        student_result = db.students.insert_one({
            "email": "student@vuquyenamerican.com",
            "password": UserModel.hash_password("student123"),
            "full_name": "Nguyen Van A",
            "role": "student",
            "status": "approved",
            "phone": "0912345678",
            "class_ids": [],
            "created_at": now,
            "updated_at": now,
        })
        student_id = student_result.inserted_id

        class_result = db.classes.insert_one({
            "name": "Lop A1 - Giao tiep co ban",
            "grade": "A1",
            "description": "Khoa hoc tieng Anh giao tiep co ban cho nguoi moi bat dau",
            "teacher_id": teacher_id,
            "student_ids": [student_id],
            "created_at": now,
            "updated_at": now,
        })
        class_id = class_result.inserted_id

        db.students.update_one(
            {"_id": student_id},
            {"$set": {"class_ids": [class_id]}},
        )

        db.courses.insert_many([
            {
                "title": "Tieng Anh Giao Tiep Co Ban",
                "description": "Khoa hoc danh cho nguoi moi bat dau, tap trung vao phat am va hoi thoai co ban.",
                "fee": "2.500.000 VND/thang",
                "duration": "3 thang",
                "image": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800",
                "is_active": True,
                "order": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "title": "Tieng Anh THPT",
                "description": "On thi THPT Quoc gia mon Tieng Anh voi phuong phap hoc hieu qua.",
                "fee": "3.000.000 VND/thang",
                "duration": "6 thang",
                "image": "https://images.unsplash.com/photo-1427504490125-794c4f59b836?w=800",
                "is_active": True,
                "order": 2,
                "created_at": now,
                "updated_at": now,
            },
            {
                "title": "IELTS Foundation",
                "description": "Xay dung nen tang vung chac cho ky thi IELTS.",
                "fee": "4.500.000 VND/thang",
                "duration": "4 thang",
                "image": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800",
                "is_active": True,
                "order": 3,
                "created_at": now,
                "updated_at": now,
            },
        ])

        db.news.insert_many([
            {
                "title": "Khai giang khoa hoc moi thang 3/2026",
                "slug": "khai-giang-khoa-hoc-moi-thang-3-2026",
                "excerpt": "Trung tam Vu Quyen American chinh thuc khai giang cac lop hoc moi.",
                "content": "<p>Trung tam Vu Quyen American tu hao thong bao khai giang cac lop hoc moi vao thang 3/2026...</p>",
                "thumbnail": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800",
                "status": "published",
                "seo_title": "Khai giang khoa hoc moi - Vu Quyen American",
                "seo_description": "Thong tin khai giang khoa hoc tieng Anh moi tai Vu Quyen American",
                "published_at": now,
                "created_at": now,
                "updated_at": now,
            },
            {
                "title": "Hoc sinh dat diem IELTS 7.5",
                "slug": "hoc-sinh-dat-diem-ielts-7-5",
                "excerpt": "Chuc mung ban Nguyen Thi B dat IELTS 7.5 sau 6 thang hoc tai trung tam.",
                "content": "<p>Day la thanh tich dang tu hao cua trung tam...</p>",
                "thumbnail": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800",
                "status": "published",
                "seo_title": "Hoc sinh dat IELTS 7.5",
                "seo_description": "Thanh tich hoc sinh Vu Quyen American",
                "published_at": now - timedelta(days=5),
                "created_at": now,
                "updated_at": now,
            },
        ])

        db.seo_settings.insert_many([
            {
                "page_key": "home",
                "meta_title": "Vu Quyen American - Trung tam Tieng Anh uy tin",
                "meta_description": "Trung tam tieng Anh Vu Quyen American - Dao tao tieng Anh giao tiep, THPT, IELTS voi phuong phap hieu qua.",
                "og_image": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200",
                "canonical_url": "https://vuquyenamerican.com",
                "created_at": now,
                "updated_at": now,
            },
            {
                "page_key": "about",
                "meta_title": "Gioi thieu - Vu Quyen American",
                "meta_description": "Tim hieu ve co Vu Quyen va trung tam tieng Anh American.",
                "og_image": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200",
                "canonical_url": "https://vuquyenamerican.com/gioi-thieu",
                "created_at": now,
                "updated_at": now,
            },
        ])

        quiz_result = db.quizzes.insert_one({
            "title": "Bai kiem tra Unit 1",
            "description": "Kiem tra tu vung va ngu phap Unit 1",
            "class_id": class_id,
            "teacher_id": teacher_id,
            "duration_minutes": 30,
            "open_at": now - timedelta(days=1),
            "close_at": now + timedelta(days=30),
            "type": "multiple_choice",
            "status": "published",
            "created_at": now,
            "updated_at": now,
        })
        quiz_id = quiz_result.inserted_id

        db.questions.insert_many([
            {
                "quiz_id": quiz_id,
                "content": "What is the capital of England?",
                "image": "",
                "options": {"A": "Paris", "B": "London", "C": "Berlin", "D": "Madrid"},
                "correct_answer": "B",
                "order": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "quiz_id": quiz_id,
                "content": "She ___ to school every day.",
                "image": "",
                "options": {"A": "go", "B": "goes", "C": "going", "D": "gone"},
                "correct_answer": "B",
                "order": 2,
                "created_at": now,
                "updated_at": now,
            },
        ])

        db.documents.insert_one({
            "title": "Tai lieu Unit 1 - Tu vung",
            "description": "Danh sach tu vung Unit 1",
            "class_name": "A1",
            "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "file_format": "pdf",
            "thumbnail": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400",
            "uploaded_by": str(teacher_id),
            "download_count": 0,
            "created_at": now,
            "updated_at": now,
        })

        video_result = db.video_lessons.insert_one({
            "title": "Video Lesson 1 - Greetings",
            "description": "Hoc cach chao hoi bang tieng Anh",
            "class_id": class_id,
            "teacher_id": teacher_id,
            "video_with_audio_url": "https://res.cloudinary.com/demo/video/upload/dog.mp4",
            "video_muted_url": "https://res.cloudinary.com/demo/video/upload/dog.mp4",
            "status": "published",
            "created_at": now,
            "updated_at": now,
        })
        video_id = video_result.inserted_id

        db.subtitles.insert_many([
            {"video_lesson_id": video_id, "start_time": 0, "end_time": 3, "text": "Hello everyone!", "created_at": now, "updated_at": now},
            {"video_lesson_id": video_id, "start_time": 3, "end_time": 6, "text": "Welcome to our lesson.", "created_at": now, "updated_at": now},
            {"video_lesson_id": video_id, "start_time": 6, "end_time": 10, "text": "Today we learn greetings.", "created_at": now, "updated_at": now},
        ])

        db.questions.insert_one({
            "video_lesson_id": video_id,
            "content": "What greeting is used in the video?",
            "options": {"A": "Goodbye", "B": "Hello everyone", "C": "See you", "D": "Thank you"},
            "correct_answer": "B",
            "type": "video_quiz",
            "created_at": now,
            "updated_at": now,
        })

        print("Seed completed!")
        print("Admin: admin@vuquyenamerican.com / admin123")
        print("Teacher: vuquyen101982@gmail.com / teacher123")
        print("Student: student@vuquyenamerican.com / student123")


if __name__ == "__main__":
    seed()
