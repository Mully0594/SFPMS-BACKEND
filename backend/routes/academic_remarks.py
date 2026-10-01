from flask import Blueprint, request, jsonify

from database import db
from models import AcademicRemark, User, Notification


academic_remarks_bp = Blueprint("academic_remarks", __name__)


FIELDS = [
    "practical_skills",
    "professional_conduct",
    "academic_progress",
    "attendance",
    "strengths",
    "improvement",
    "remarks",
    "recommendation",
    "rating",
]


def _apply_fields(remark, data):
    for field in FIELDS:
        if field in data:
            setattr(remark, field, data[field])


@academic_remarks_bp.route("/", methods=["POST"])
def create_remark():

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

    # One remark record per student/supervisor - update in place if
    # it already exists (matches the frontend "edit remarks" flow).
    remark = AcademicRemark.query.filter_by(
        student_id=student_id,
        supervisor_id=supervisor_id
    ).first()

    is_new = remark is None

    if is_new:
        remark = AcademicRemark(
            student_id=student_id,
            supervisor_id=supervisor_id,
            placement_id=data.get("placement_id")
        )
        db.session.add(remark)

    _apply_fields(remark, data)
    remark.submitted = data.get("submitted", True)

    if is_new:
        db.session.add(Notification(
            user_id=student_id,
            message="Your academic supervisor has submitted remarks on your placement.",
            type="ACADEMIC_REMARK"
        ))

    db.session.commit()

    return jsonify({
        "message": "Academic remarks saved successfully",
        "remark": remark.to_dict()
    }), 201 if is_new else 200


@academic_remarks_bp.route("/", methods=["GET"])
def get_remarks():

    query = AcademicRemark.query

    student_id = request.args.get("student_id")
    supervisor_id = request.args.get("supervisor_id")

    if student_id:
        query = query.filter(AcademicRemark.student_id == student_id)

    if supervisor_id:
        query = query.filter(AcademicRemark.supervisor_id == supervisor_id)

    remarks = query.order_by(AcademicRemark.id.desc()).all()

    return jsonify([remark.to_dict() for remark in remarks]), 200


@academic_remarks_bp.route("/<int:remark_id>", methods=["GET"])
def get_remark(remark_id):

    remark = AcademicRemark.query.get(remark_id)

    if not remark:
        return jsonify({"message": "Remark not found"}), 404

    return jsonify(remark.to_dict()), 200
