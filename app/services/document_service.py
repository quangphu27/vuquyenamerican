from app.repositories.document_repository import DocumentRepository
from app.utils.helpers import serialize_doc, paginate
from app.utils.cloudinary_util import upload_file


class DocumentService:
    def __init__(self):
        self.repo = DocumentRepository()

    def list_documents(self, keyword="", class_filter=None, page=1, per_page=10):
        def query(skip, limit):
            return self.repo.search(keyword, class_filter, skip, limit)

        return paginate(query, page, per_page)

    def get_document(self, doc_id):
        return serialize_doc(self.repo.find_by_id(doc_id))

    def create_document(self, data, file=None, thumbnail=None, uploaded_by=None):
        file_info = upload_file(file, subfolder="documents") if file else None
        thumb_info = upload_file(thumbnail, subfolder="documents/thumbs") if thumbnail else None

        doc_data = {
            "title": data["title"],
            "description": data.get("description", ""),
            "class_name": data.get("class_name", ""),
            "file_url": file_info["url"] if file_info else data.get("file_url", ""),
            "file_public_id": file_info["public_id"] if file_info else "",
            "file_format": file_info["format"] if file_info else data.get("file_format", ""),
            "thumbnail": thumb_info["url"] if thumb_info else data.get("thumbnail", ""),
            "uploaded_by": uploaded_by,
            "download_count": 0,
        }
        doc = self.repo.create(doc_data)
        return serialize_doc(doc)

    def update_document(self, doc_id, data, file=None, thumbnail=None):
        update_data = {
            k: data[k] for k in ("title", "description", "class_name") if k in data
        }
        if file:
            file_info = upload_file(file, subfolder="documents")
            if file_info:
                update_data["file_url"] = file_info["url"]
                update_data["file_public_id"] = file_info["public_id"]
                update_data["file_format"] = file_info["format"]
        if thumbnail:
            thumb_info = upload_file(thumbnail, subfolder="documents/thumbs")
            if thumb_info:
                update_data["thumbnail"] = thumb_info["url"]
        doc = self.repo.update(doc_id, update_data)
        return serialize_doc(doc)

    def increment_download(self, doc_id):
        from app.extensions import get_db
        get_db().documents.update_one({"_id": self.repo.find_by_id(doc_id)["_id"]}, {"$inc": {"download_count": 1}})
        return self.get_document(doc_id)

    def delete_document(self, doc_id):
        return self.repo.delete(doc_id)
