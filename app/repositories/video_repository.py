from bson import ObjectId
from app.repositories.base_repository import BaseRepository


class VideoLessonRepository(BaseRepository):
    collection_name = "video_lessons"

    def find_by_class(self, class_id, skip=0, limit=20):
        return self.find_all({"class_id": ObjectId(class_id)}, skip, limit, sort=[("created_at", -1)])


class SubtitleRepository(BaseRepository):
    collection_name = "subtitles"

    def find_by_video(self, video_lesson_id):
        items, _ = self.find_all(
            {"video_lesson_id": ObjectId(video_lesson_id)}, 0, 1000, sort=[("start_time", 1)]
        )
        return items

    def delete_by_video(self, video_lesson_id):
        self.collection.delete_many({"video_lesson_id": ObjectId(video_lesson_id)})


class AudioRecordRepository(BaseRepository):
    collection_name = "audio_records"

    def find_by_student_lesson(self, student_id, video_lesson_id):
        return self.collection.find_one({
            "student_id": ObjectId(student_id),
            "video_lesson_id": ObjectId(video_lesson_id),
        })


class VideoProgressRepository(BaseRepository):
    collection_name = "video_lesson_progress"

    def find_by_student_lesson(self, student_id, video_lesson_id):
        return self.collection.find_one({
            "student_id": ObjectId(student_id),
            "video_lesson_id": ObjectId(video_lesson_id),
        })

    def upsert_steps(self, student_id, video_lesson_id, completed_steps):
        from app.utils.helpers import utcnow
        self.collection.update_one(
            {
                "student_id": ObjectId(student_id),
                "video_lesson_id": ObjectId(video_lesson_id),
            },
            {
                "$set": {
                    "completed_steps": completed_steps,
                    "updated_at": utcnow(),
                },
                "$setOnInsert": {
                    "student_id": ObjectId(student_id),
                    "video_lesson_id": ObjectId(video_lesson_id),
                    "created_at": utcnow(),
                },
            },
            upsert=True,
        )
        return self.find_by_student_lesson(student_id, video_lesson_id)
