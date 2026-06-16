from app.repositories.base_repository import BaseRepository


class NewsRepository(BaseRepository):
    collection_name = "news"

    def find_published(self, skip=0, limit=10):
        return self.find_all(
            {"status": "published"}, skip, limit, sort=[("published_at", -1)]
        )

    def find_by_slug(self, slug):
        return self.collection.find_one({"slug": slug, "status": "published"})


class SeoRepository(BaseRepository):
    collection_name = "seo_settings"

    def find_by_page(self, page_key):
        return self.collection.find_one({"page_key": page_key})

    def upsert_page(self, page_key, data):
        from app.utils.helpers import utcnow
        data["page_key"] = page_key
        data["updated_at"] = utcnow()
        self.collection.update_one(
            {"page_key": page_key},
            {"$set": data, "$setOnInsert": {"created_at": utcnow()}},
            upsert=True,
        )
        return self.find_by_page(page_key)


class CourseRepository(BaseRepository):
    collection_name = "courses"

    def find_active(self, skip=0, limit=20):
        return self.find_all({"is_active": True}, skip, limit, sort=[("order", 1)])


class ContactRepository(BaseRepository):
    collection_name = "contacts"
