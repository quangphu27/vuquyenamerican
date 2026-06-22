from bson import ObjectId
from app.repositories.base_repository import BaseRepository


class VideoLessonRepository(BaseRepository):
    collection_name = "video_lessons"

    def find_by_class(self, class_id, skip=0, limit=20):
        return self.find_all({"class_id": ObjectId(class_id)}, skip, limit, sort=[("created_at", -1)])

    def find_by_story(self, story_id, skip=0, limit=100):
        return self.find_all(
            {"story_id": ObjectId(story_id)},
            skip,
            limit,
            sort=[("episode_number", 1), ("created_at", 1)],
        )

    def count_by_story(self, story_id):
        return self.count({"story_id": ObjectId(story_id)})

    def count_by_level(self, level):
        return self.count({"level": int(level), "status": "published"})


class VideoStoryRepository(BaseRepository):
    collection_name = "video_stories"

    def find_by_level(self, level, skip=0, limit=100):
        return self.find_all(
            {"level": int(level)},
            skip,
            limit,
            sort=[("order", 1), ("title", 1)],
        )

    def count_by_level(self, level):
        return self.count({"level": int(level)})


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
