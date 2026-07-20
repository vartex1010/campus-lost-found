import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, LostItem, FoundItem

items_bp = Blueprint("items", __name__)


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _save_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    if not _allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file_storage.save(path)
    return filename


@items_bp.route("/api/report-lost", methods=["POST"])
@jwt_required()
def report_lost():
    user_id = int(get_jwt_identity())
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    image_path = _save_image(request.files.get("image"))

    item = LostItem(
        user_id=user_id, title=title, description=description,
        location=location, image_path=image_path,
    )
    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


@items_bp.route("/api/report-found", methods=["POST"])
@jwt_required()
def report_found():
    user_id = int(get_jwt_identity())
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    image_path = _save_image(request.files.get("image"))

    item = FoundItem(
        user_id=user_id, title=title, description=description,
        location=location, image_path=image_path,
    )
    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


@items_bp.route("/api/items", methods=["GET"])
def search_items():
    kind = request.args.get("type", "all")  # lost | found | all
    q = request.args.get("q", "").strip()

    results = []
    if kind in ("lost", "all"):
        query = LostItem.query
        if q:
            query = query.filter(LostItem.title.ilike(f"%{q}%") | LostItem.description.ilike(f"%{q}%"))
        results += [{"type": "lost", **i.to_dict()} for i in query.order_by(LostItem.created_at.desc()).all()]

    if kind in ("found", "all"):
        query = FoundItem.query
        if q:
            query = query.filter(FoundItem.title.ilike(f"%{q}%") | FoundItem.description.ilike(f"%{q}%"))
        results += [{"type": "found", **i.to_dict()} for i in query.order_by(FoundItem.created_at.desc()).all()]

    results.sort(key=lambda x: x["created_at"], reverse=True)
    return jsonify(results), 200


@items_bp.route("/api/my-reports", methods=["GET"])
@jwt_required()
def my_reports():
    user_id = int(get_jwt_identity())
    lost = [{"type": "lost", **i.to_dict()} for i in LostItem.query.filter_by(user_id=user_id).all()]
    found = [{"type": "found", **i.to_dict()} for i in FoundItem.query.filter_by(user_id=user_id).all()]
    combined = lost + found
    combined.sort(key=lambda x: x["created_at"], reverse=True)
    return jsonify(combined), 200
