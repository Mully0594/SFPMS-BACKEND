from flask import Blueprint, request, jsonify

from database import db
from models import FieldEvaluation, User, Notification


evaluations_bp = Blueprint("evaluations", __name__)


SCORE_FIELDS = [
    "attendance_score",
    "discipline_score",
    "skills_score",
    "teamwork_score",
    "overall_score",
]


def _apply_scores(evaluation, data):
    for field in SCORE_FIELDS:
        if field in data:
            setattr(evaluation, field, data[field])

    if "comments" in data:
        evaluation.comments = data["comments"]


@evaluations_bp.route("/", methods=["POST"])
def create_evaluation():

    data = request.get_json()

    student_id = data.get("student_id")
    supervisor_id = data.get("supervisor_id")

    if not student_id or not supervisor_id:
        return jsonify({
            "message": "student_id and supervisor_id are required"
        }), 400

    if not User.query.get(student_id):
        return jsonify({"message": "Student not found"}), 404

    if not User.query.get(supervisor_id):
        return jsonify({"message": "Supervisor not found"}), 404

    # One evaluation per student/supervisor pair - update if it
    # already exists instead of creating a duplicate.
    evaluation = FieldEvaluation.query.filter_by(
        student_id=student_id,
        supervisor_id=supervisor_id
    ).first()

    is_new = evaluation is None

    if is_new:
        evaluation = FieldEvaluation(
            student_id=student_id,
            supervisor_id=supervisor_id,
            placement_id=data.get("placement_id")
        )
        db.session.add(evaluation)

    _apply_scores(evaluation, data)
    evaluation.status = data.get("status", "COMPLETED")

    if is_new:
        db.session.add(Notification(
            user_id=student_id,
            message="Your field supervisor has submitted your evaluation.",
            type="EVALUATION"
        ))

    db.session.commit()

    return jsonify({
        "message": "Evaluation saved successfully",
        "evaluation": evaluation.to_dict()
    }), 201 if is_new else 200


@evaluations_bp.route("/", methods=["GET"])
def get_evaluations():

    query = FieldEvaluation.query

    student_id = request.args.get("student_id")
    supervisor_id = request.args.get("supervisor_id")

    if student_id:
        query = query.filter(FieldEvaluation.student_id == student_id)

    if supervisor_id:
        query = query.filter(FieldEvaluation.supervisor_id == supervisor_id)

    evaluations = query.order_by(FieldEvaluation.id.desc()).all()

    return jsonify([evaluation.to_dict() for evaluation in evaluations]), 200


@evaluations_bp.route("/<int:evaluation_id>", methods=["GET"])
def get_evaluation(evaluation_id):

    evaluation = FieldEvaluation.query.get(evaluation_id)

    if not evaluation:
        return jsonify({"message": "Evaluation not found"}), 404

    return jsonify(evaluation.to_dict()), 200
