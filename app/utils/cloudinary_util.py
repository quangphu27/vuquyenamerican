import cloudinary
import cloudinary.uploader
from flask import current_app


def init_cloudinary(app):
    cloudinary_url = app.config.get("CLOUDINARY_URL")
    if cloudinary_url:
        cloudinary.config(cloudinary_url=cloudinary_url, secure=True)


def cloudinary_folder(subfolder=None):
    prefix = current_app.config.get("CLOUDINARY_FOLDER_PREFIX", "vuquyenamerican")
    if subfolder:
        return f"{prefix}/{subfolder}"
    return prefix


def normalize_video_url(url):
    if not url or "res.cloudinary.com" not in url:
        return url
    if "/video/upload/" in url and "/f_mp4" not in url and "/f_auto" not in url and "/vc_h264" not in url:
        return url.replace("/video/upload/", "/video/upload/f_mp4,vc_h264/")
    return url


def upload_file(file, subfolder=None, resource_type="auto"):
    if not file:
        return None
    if not current_app.config.get("CLOUDINARY_URL"):
        current_app.logger.warning("CLOUDINARY_URL chua duoc cau hinh")
        return None
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=cloudinary_folder(subfolder),
            resource_type=resource_type,
        )
        url = result.get("secure_url")
        if resource_type == "video" and url:
            url = normalize_video_url(url)
        return {
            "url": url,
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
            "resource_type": result.get("resource_type"),
        }
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload error: {e}")
        return None


def delete_file(public_id, resource_type="image"):
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception:
        return False
