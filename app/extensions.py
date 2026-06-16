from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from pymongo import MongoClient

jwt = JWTManager()
cors = CORS()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
mongo_client: MongoClient | None = None
db = None


def get_db():
    if db is None:
        raise RuntimeError("Database chưa được khởi tạo. Hãy gọi create_app() trước.")
    return db


def init_extensions(app):
    global mongo_client, db

    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    mail.init_app(app)
    limiter.init_app(app)
    limiter.default_limits = [app.config["RATE_LIMIT_DEFAULT"]]

    mongo_client = MongoClient(app.config["MONGODB_URI"])
    db = mongo_client[app.config["MONGODB_DB"]]
