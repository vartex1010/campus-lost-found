import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db

from routes.auth import auth_bp
from routes.items import items_bp
from routes.matches import matches_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(app)  # allow the frontend (served separately) to call the API
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(matches_bp)

    # Serve uploaded images
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Serve the frontend HTML directly (optional convenience)
    @app.route("/")
    def index():
        return send_from_directory(os.path.dirname(__file__), "campus-lost-found.html")

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
