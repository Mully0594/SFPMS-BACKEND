from flask import Blueprint, request, jsonify

from database import db
from models import LogReview, DailyLog, User, Notification


log_reviews_bp = Blueprint("log_reviews", __name__)


@log_reviews_bp.route("/", methods=["POST"])
def create_log_review():

    data = request.get_json()

    log_id = data.get("log_id")
    supervisor_id = data.get("supervisor_id")
    decision = data.get("decision")
    comment = data.get("comment")

    if not log_id or not supervisor_id or not decision:
        return jsonify({
            "message": "log_id, supervisor_id and decision are required"
        }), 400

    daily_log = DailyLog.query.get(log_id)

    if not daily_log:
        return jsonify({"message": "Daily log not found"}), 404

    supervisor = User.query.get(supervisor_id)

    if not supervisor:
        return jsonify({"message": "Supervisor not found"}), 404

    decision = decision.upper()

    if decision not in ["APPROVED", "REJECTED"]:
        return jsonify({
            "message": "decision must be APPROVED or REJECTED"
        }), 400

    review = LogReview(
        log_id=log_id,
        supervisor_id=supervisor_id,
        comment=comment,
        decision=decision
    )

    db.session.add(review)

    # Keep the log's status in sync with the latest review decision
    daily_log.status = decision

    db.session.add(Notification(
        user_id=daily_log.student_id,
        message=f"Your daily log for {daily_log.log_date} was {decision.lower()}.",
        type="LOGBOOK"
    ))

    db.session.commit()

    return jsonify({
        "message": "Log review submitted successfully",
        "review": review.to_dict()
    }), 201


@log_reviews_bp.route("/", methods=["GET"])
def get_log_reviews():

    query = LogReview.query

    log_id = request.args.get("log_id")
    supervisor_id = request.args.get("supervisor_id")

    if log_id:
        query = query.filter(LogReview.log_id == log_id)

    if supervisor_id:
        query = query.filter(LogReview.supervisor_id == supervisor_id)

    reviews = query.order_by(LogReview.reviewed_at.desc()).all()

    return jsonify([review.to_dict() for review in reviews]), 200
