import os
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from models import db, LostItem, FoundItem, Match
from ml.text_match import text_similarity
from ml.image_match import image_similarity

matches_bp = Blueprint("matches", __name__)


def _full_image_path(filename):
    if not filename:
        return None
    return os.path.join(current_app.config["UPLOAD_FOLDER"], filename)


@matches_bp.route("/api/run-matching", methods=["POST"])
@jwt_required()
def run_matching():
    """
    Compares every open lost item against every open found item,
    scores them, and stores/updates Match rows above the threshold.
    Call this after a new report is filed, or on a schedule/cron.
    """
    threshold = current_app.config["MATCH_THRESHOLD"]
    lost_items = LostItem.query.filter_by(status="open").all()
    found_items = FoundItem.query.filter_by(status="open").all()

    created = 0
    for lost in lost_items:
        for found in found_items:
            exists = Match.query.filter_by(lost_item_id=lost.id, found_item_id=found.id).first()
            if exists:
                continue

            t_score = text_similarity(
                {"title": lost.title, "description": lost.description, "location": lost.location},
                {"title": found.title, "description": found.description, "location": found.location},
            )
            i_score = image_similarity(
                _full_image_path(lost.image_path), _full_image_path(found.image_path)
            )

            # Combine: weight image score higher when available
            if i_score is not None:
                combined = 0.4 * t_score + 0.6 * i_score
            else:
                combined = t_score
                i_score = 0.0

            if combined >= threshold:
                match = Match(
                    lost_item_id=lost.id, found_item_id=found.id,
                    text_score=t_score, image_score=i_score, combined_score=combined,
                )
                db.session.add(match)
                created += 1

    db.session.commit()
    return jsonify({"new_matches": created}), 200


@matches_bp.route("/api/matches", methods=["GET"])
def list_matches():
    matches = Match.query.filter_by(status="pending").order_by(Match.combined_score.desc()).all()
    return jsonify([m.to_dict() for m in matches]), 200


@matches_bp.route("/api/matches/<int:match_id>/confirm", methods=["POST"])
@jwt_required()
def confirm_match(match_id):
    match = Match.query.get_or_404(match_id)
    match.status = "confirmed"
    match.lost_item.status = "matched"
    match.found_item.status = "matched"
    db.session.commit()
    return jsonify(match.to_dict()), 200


@matches_bp.route("/api/matches/<int:match_id>/reject", methods=["POST"])
@jwt_required()
def reject_match(match_id):
    match = Match.query.get_or_404(match_id)
    match.status = "rejected"
    db.session.commit()
    return jsonify(match.to_dict()), 200
