from bson import ObjectId
from app.extensions import get_db
from app.utils.helpers import utcnow


class BaseRepository:
    collection_name = None

    @property
    def collection(self):
        return get_db()[self.collection_name]

    def find_by_id(self, id_str):
        return self.collection.find_one({"_id": ObjectId(id_str)})

    def find_all(self, filter_query=None, skip=0, limit=10, sort=None):
        filter_query = filter_query or {}
        cursor = self.collection.find(filter_query)
        if sort:
            cursor = cursor.sort(sort)
        total = self.collection.count_documents(filter_query)
        items = list(cursor.skip(skip).limit(limit))
        return items, total

    def create(self, data):
        data["created_at"] = utcnow()
        data["updated_at"] = utcnow()
        result = self.collection.insert_one(data)
        return self.find_by_id(result.inserted_id)

    def update(self, id_str, data):
        data["updated_at"] = utcnow()
        self.collection.update_one({"_id": ObjectId(id_str)}, {"$set": data})
        return self.find_by_id(id_str)

    def delete(self, id_str):
        result = self.collection.delete_one({"_id": ObjectId(id_str)})
        return result.deleted_count > 0

    def count(self, filter_query=None):
        return self.collection.count_documents(filter_query or {})
