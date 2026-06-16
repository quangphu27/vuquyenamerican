from app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository):
    collection_name = "documents"

    def search(self, keyword, class_filter=None, skip=0, limit=10):
        filter_q = {}
        if keyword:
            filter_q["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
            ]
        if class_filter:
            filter_q["class_name"] = class_filter
        return self.find_all(filter_q, skip, limit, sort=[("created_at", -1)])
