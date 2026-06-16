from datetime import datetime
from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
from app.config import Config
from app.extensions import init_extensions, jwt
from app.utils.cloudinary_util import init_cloudinary


class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.json = MongoJSONProvider(app)
    app.config.from_object(config_class)

    init_extensions(app)
    init_cloudinary(app)

    from app.routes.auth_routes import bp as auth_bp
    from app.routes.user_routes import bp as user_bp
    from app.routes.class_routes import bp as class_bp
    from app.routes.document_routes import bp as document_bp
    from app.routes.quiz_routes import bp as quiz_bp
    from app.routes.video_routes import bp as video_bp
    from app.routes.content_routes import bp as content_bp
    from app.routes.dashboard_routes import bp as dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "Vũ Quyên American API"}), 200

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"message": "Token hết hạn"}), 401

    @jwt.invalid_token_loader
    def invalid_token(error):
        return jsonify({"message": "Token không hợp lệ"}), 401

    @jwt.unauthorized_loader
    def missing_token(error):
        return jsonify({"message": "Thiếu token xác thực"}), 401

    return app
