from bson import ObjectId
from app.repositories.video_repository import (
    VideoLessonRepository,
    SubtitleRepository,
    AudioRecordRepository,
    VideoProgressRepository,
    VideoStoryRepository,
)
from app.repositories.quiz_repository import QuestionRepository
from app.utils.helpers import serialize_doc
from app.utils.cloudinary_util import upload_file, normalize_video_url

VIDEO_STEPS = ["listen", "read", "dub", "quiz"]


class VideoService:
    def __init__(self):
        self.video_repo = VideoLessonRepository()
        self.subtitle_repo = SubtitleRepository()
        self.audio_repo = AudioRecordRepository()
        self.progress_repo = VideoProgressRepository()
        self.story_repo = VideoStoryRepository()
        self.question_repo = QuestionRepository()

    def list_levels(self):
        levels = []
        for level in range(1, 10):
            story_count = self.story_repo.count_by_level(level)
            episode_count = self.video_repo.count_by_level(level)
            levels.append({
                "level": level,
                "story_count": story_count,
                "episode_count": episode_count,
            })
        return levels

    def list_stories(self, level):
        items, total = self.story_repo.find_by_level(level)
        result = []
        for story in items:
            doc = serialize_doc(story)
            doc["episode_count"] = self.video_repo.count_by_story(str(story["_id"]))
            result.append(doc)
        return {"items": result, "level": int(level), "total": total}

    def list_episodes(self, story_id):
        story = self.story_repo.find_by_id(story_id)
        if not story:
            return None
        items, total = self.video_repo.find_by_story(story_id)
        published = [v for v in items if v.get("status") == "published"]
        return {
            "story": serialize_doc(story),
            "items": [serialize_doc(v) for v in published],
            "total": len(published),
        }

    def create_story(self, data, teacher_id):
        level = int(data.get("level", 1))
        if level < 1 or level > 9:
            raise ValueError("Level phải từ 1 đến 9")
        story = self.story_repo.create({
            "level": level,
            "title": data["title"].strip(),
            "description": data.get("description", "").strip(),
            "thumbnail": data.get("thumbnail", ""),
            "order": int(data.get("order") or 0),
            "teacher_id": ObjectId(teacher_id),
        })
        return serialize_doc(story)

    def update_story(self, story_id, data):
        story = self.story_repo.find_by_id(story_id)
        if not story:
            return None
        allowed = {"title", "description", "thumbnail", "order", "level"}
        update_data = {k: v for k, v in data.items() if k in allowed and v not in (None, "")}
        if "level" in update_data:
            update_data["level"] = int(update_data["level"])
        if "order" in update_data:
            update_data["order"] = int(update_data["order"])
        if not update_data:
            return serialize_doc(story)
        updated = self.story_repo.update(story_id, update_data)
        return serialize_doc(updated)

    def delete_story(self, story_id):
        episodes, _ = self.video_repo.find_by_story(story_id, 0, 500)
        for ep in episodes:
            self.delete_lesson(str(ep["_id"]))
        return self.story_repo.delete(story_id)

    def list_lessons(self, class_id=None, page=1, per_page=20):
        skip = (page - 1) * per_page
        if class_id:
            items, total = self.video_repo.find_by_class(class_id, skip, per_page)
        else:
            items, total = self.video_repo.find_all({}, skip, per_page, sort=[("created_at", -1)])
        return {
            "items": [serialize_doc(v) for v in items],
            "pagination": {"page": page, "per_page": per_page, "total": total},
        }

    def get_lesson(self, lesson_id, include_quiz=False):
        lesson = self.video_repo.find_by_id(lesson_id)
        if not lesson:
            return None
        subtitles = self.subtitle_repo.find_by_video(lesson_id)
        result = serialize_doc(lesson)
        if result.get("video_with_audio_url"):
            result["video_with_audio_url"] = normalize_video_url(result["video_with_audio_url"])
        if result.get("video_muted_url"):
            result["video_muted_url"] = normalize_video_url(result["video_muted_url"])
        result["subtitles"] = serialize_doc(subtitles)
        if include_quiz:
            questions, _ = self.question_repo.find_all(
                {"video_lesson_id": ObjectId(lesson_id)}, 0, 100
            )
            for q in questions:
                q.pop("correct_answer", None)
            result["quiz_questions"] = serialize_doc(questions)
        return result

    def create_lesson(self, data, teacher_id, video_with_audio=None, video_muted=None):
        audio_info = upload_file(video_with_audio, subfolder="videos", resource_type="video") if video_with_audio else None
        muted_info = upload_file(video_muted, subfolder="videos", resource_type="video") if video_muted else None

        title = data.get("title") or data.get("episode_title") or "Bài học video"
        lesson_data = {
            "title": title,
            "description": data.get("description", ""),
            "teacher_id": ObjectId(teacher_id),
            "video_with_audio_url": audio_info["url"] if audio_info else data.get("video_with_audio_url", ""),
            "video_muted_url": muted_info["url"] if muted_info else data.get("video_muted_url", ""),
            "status": data.get("status", "draft"),
        }

        if data.get("story_id"):
            story = self.story_repo.find_by_id(data["story_id"])
            if not story:
                raise ValueError("Không tìm thấy truyện")
            lesson_data["story_id"] = ObjectId(data["story_id"])
            lesson_data["level"] = int(data.get("level") or story.get("level") or 1)
            lesson_data["episode_number"] = int(data.get("episode_number") or 1)
            lesson_data["episode_title"] = data.get("episode_title", title)
        elif data.get("class_id"):
            lesson_data["class_id"] = ObjectId(data["class_id"])
        else:
            raise ValueError("Cần chọn truyện hoặc lớp học")

        lesson = self.video_repo.create(lesson_data)
        return serialize_doc(lesson)

    def update_lesson(self, lesson_id, data, video_with_audio=None, video_muted=None):
        lesson = self.video_repo.find_by_id(lesson_id)
        if not lesson:
            return None

        allowed = {"title", "description", "status", "class_id", "story_id", "level", "episode_number", "episode_title"}
        update_data = {k: v for k, v in data.items() if k in allowed and v not in (None, "")}
        if "class_id" in update_data:
            update_data["class_id"] = ObjectId(update_data["class_id"])
        if "story_id" in update_data:
            update_data["story_id"] = ObjectId(update_data["story_id"])
        if "level" in update_data:
            update_data["level"] = int(update_data["level"])
        if "episode_number" in update_data:
            update_data["episode_number"] = int(update_data["episode_number"])

        if video_with_audio:
            audio_info = upload_file(video_with_audio, subfolder="videos", resource_type="video")
            if audio_info:
                update_data["video_with_audio_url"] = audio_info["url"]
        if video_muted:
            muted_info = upload_file(video_muted, subfolder="videos", resource_type="video")
            if muted_info:
                update_data["video_muted_url"] = muted_info["url"]

        if not update_data:
            return serialize_doc(lesson)

        updated = self.video_repo.update(lesson_id, update_data)
        return serialize_doc(updated)

    def add_subtitle(self, lesson_id, data):
        sub_data = {
            "video_lesson_id": ObjectId(lesson_id),
            "start_time": float(data["start_time"]),
            "end_time": float(data["end_time"]),
            "text": data["text"],
        }
        sub = self.subtitle_repo.create(sub_data)
        return serialize_doc(sub)

    def update_subtitle(self, subtitle_id, data):
        allowed = {"start_time", "end_time", "text"}
        update_data = {k: v for k, v in data.items() if k in allowed}
        if "start_time" in update_data:
            update_data["start_time"] = float(update_data["start_time"])
        if "end_time" in update_data:
            update_data["end_time"] = float(update_data["end_time"])
        sub = self.subtitle_repo.update(subtitle_id, update_data)
        return serialize_doc(sub)

    def delete_subtitle(self, subtitle_id):
        return self.subtitle_repo.delete(subtitle_id)

    def bulk_save_subtitles(self, lesson_id, subtitles):
        self.subtitle_repo.delete_by_video(lesson_id)
        created = []
        for s in subtitles:
            sub = self.subtitle_repo.create({
                "video_lesson_id": ObjectId(lesson_id),
                "start_time": float(s["start_time"]),
                "end_time": float(s["end_time"]),
                "text": s["text"],
            })
            created.append(serialize_doc(sub))
        return created

    def add_video_quiz_question(self, lesson_id, data):
        q_data = {
            "video_lesson_id": ObjectId(lesson_id),
            "content": data["content"],
            "options": data["options"],
            "correct_answer": data["correct_answer"],
            "type": "video_quiz",
        }
        q = self.question_repo.create(q_data)
        return serialize_doc(q)

    def save_audio_record(self, student_id, lesson_id, audio_file):
        audio_info = upload_file(audio_file, subfolder="audio", resource_type="video")
        if not audio_info:
            return None, "Upload thất bại"

        existing = self.audio_repo.find_by_student_lesson(student_id, lesson_id)
        record_data = {
            "student_id": ObjectId(student_id),
            "video_lesson_id": ObjectId(lesson_id),
            "audio_url": audio_info["url"],
            "audio_public_id": audio_info["public_id"],
        }
        if existing:
            record = self.audio_repo.update(str(existing["_id"]), record_data)
        else:
            record = self.audio_repo.create(record_data)
        self._auto_complete_step(student_id, lesson_id, "dub")
        return serialize_doc(record), None

    def submit_video_quiz(self, lesson_id, student_id, answers):
        questions, _ = self.question_repo.find_all(
            {"video_lesson_id": ObjectId(lesson_id)}, 0, 100
        )
        correct = 0
        detail = []
        for q in questions:
            qid = str(q["_id"])
            student_ans = answers.get(qid, "")
            is_correct = student_ans == q.get("correct_answer")
            if is_correct:
                correct += 1
            detail.append({
                "question_id": qid,
                "is_correct": is_correct,
                "student_answer": student_ans,
            })
        total = len(questions)
        if student_id:
            self._auto_complete_step(student_id, lesson_id, "quiz")
        return {
            "correct": correct,
            "total": total,
            "score": round((correct / total) * 10, 1) if total else 0,
            "detail": detail,
        }

    def _normalize_progress(self, progress):
        completed = progress.get("completed_steps", []) if progress else []
        completed = [s for s in VIDEO_STEPS if s in completed]
        current = next((s for s in VIDEO_STEPS if s not in completed), None)
        return {"completed_steps": completed, "current_step": current}

    def get_progress(self, student_id, lesson_id):
        progress = self.progress_repo.find_by_student_lesson(student_id, lesson_id)
        result = self._normalize_progress(progress)
        if self.audio_repo.find_by_student_lesson(student_id, lesson_id):
            if "dub" not in result["completed_steps"]:
                result["completed_steps"].append("dub")
        return self._normalize_progress({"completed_steps": result["completed_steps"]})

    def can_access_step(self, student_id, lesson_id, step):
        if step not in VIDEO_STEPS:
            return False, "Bước học không hợp lệ"
        progress = self.get_progress(student_id, lesson_id)
        completed = progress["completed_steps"]
        idx = VIDEO_STEPS.index(step)
        if idx == 0:
            return True, None
        prev = VIDEO_STEPS[idx - 1]
        if prev not in completed:
            return False, f"Vui lòng hoàn thành bước {idx} trước"
        return True, None

    def complete_step(self, student_id, lesson_id, step):
        if step not in VIDEO_STEPS:
            return None, "Bước học không hợp lệ"

        ok, error = self.can_access_step(student_id, lesson_id, step)
        if not ok:
            return None, error

        progress = self.get_progress(student_id, lesson_id)
        completed = list(progress["completed_steps"])
        if step not in completed:
            completed.append(step)
        saved = self.progress_repo.upsert_steps(student_id, lesson_id, completed)
        return serialize_doc(self._normalize_progress(saved)), None

    def _auto_complete_step(self, student_id, lesson_id, step):
        progress = self.get_progress(student_id, lesson_id)
        completed = list(progress["completed_steps"])
        if step in completed:
            return
        ok, _ = self.can_access_step(student_id, lesson_id, step)
        if ok:
            completed.append(step)
            self.progress_repo.upsert_steps(student_id, lesson_id, completed)

    def delete_lesson(self, lesson_id):
        self.subtitle_repo.delete_by_video(lesson_id)
        self.question_repo.collection.delete_many({"video_lesson_id": ObjectId(lesson_id)})
        return self.video_repo.delete(lesson_id)
