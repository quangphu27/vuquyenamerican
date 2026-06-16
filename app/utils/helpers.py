from datetime import datetime, timezone
from bson import ObjectId


def utcnow():
    return datetime.now(timezone.utc)


def ensure_utc(dt):
    """Chuẩn hóa datetime để so sánh (MongoDB thường lưu naive UTC)."""
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = dt.strip()
        if not dt:
            return None
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def serialize_doc(doc):
    if doc is None:
        return None
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            result[key] = serialize_doc(value)
        return result
    return doc


def to_object_id(id_str):
    if not id_str:
        return None
    try:
        return ObjectId(id_str)
    except Exception:
        return None


def paginate(query_fn, page=1, per_page=10):
    page = max(1, int(page))
    per_page = min(100, max(1, int(per_page)))
    skip = (page - 1) * per_page
    items, total = query_fn(skip, per_page)
    return {
        "items": serialize_doc(items),
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page if total else 0,
        },
    }
