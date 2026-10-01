from datetime import datetime

from flask import Blueprint, request, jsonify

from database import db
from models import Report, User, Placement, Notification
from utils.uploads import save_upload

reports_bp = Blueprint("reports", __name__)

VALID_STATUSES = {"PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED"}


def _get_input():
    if request.content_type and "multipart/form-data" in request.content_type:
        return request.form
    return request.get_json() or {}


def _get_student(student_id):
    try:
        student_id = int(student_id)
    except (TypeError, ValueError):
        return None

    student = User.query.get(student_id)

    if not student:
        return None

    if student.role != "STUDENT":
        return None

    return student


@reports_bp.route("/", methods=["POST"])
def create_report():
    data = _get_input()

    student_id = data.get("student_id")
    placement_id = data.get("placement_id")

    if not student_id or not placement_id:
        return jsonify({
            "message": "student_id and placement_id are required"
        }), 400

    student = _get_student(student_id)

    if not student:
        return jsonify({
            "message": "Valid student not found"
        }), 404

    try:
        placement_id = int(placement_id)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Invalid placement_id"
        }), 400

    placement = Placement.query.get(placement_id)

    if not placement:
        return jsonify({
            "message": "Placement not found"
        }), 404

    if placement.student_id != student.id:
        return jsonify({
            "message": "This placement does not belong to this student"
        }), 403

    if placement.status != "ACTIVE":
        return jsonify({
            "message": "Reports can only be submitted for an active placement"
        }), 400

    report = Report(
        student_id=student.id,
        placement_id=placement.id,
        title=data.get("title"),
        description=data.get("description"),
        report_type=data.get("report_type", "General"),
        status="PENDING"
    )

    if request.files.get("file"):
        try:
            report.file_path = save_upload(
                request.files.get("file"),
                "reports"
            )
        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

    db.session.add(report)
    db.session.flush()

    db.session.add(
        Notification(
            user_id=student.id,
            message=f"Your report '{report.title or report.report_type}' has been submitted successfully.",
            type="REPORT"
        )
    )

    db.session.commit()

    return jsonify({
        "message": "Report submitted successfully",
        "report": report.to_dict()
    }), 201


@reports_bp.route("/", methods=["GET"])
def get_reports():
    query = Report.query

    student_id = request.args.get("student_id")
    placement_id = request.args.get("placement_id")
    status = request.args.get("status")
    report_type = request.args.get("report_type")

    if student_id:
        query = query.filter(
            Report.student_id == int(student_id)
        )

    if placement_id:
        query = query.filter(
            Report.placement_id == int(placement_id)
        )

    if status:
        status = status.upper()

        if status not in VALID_STATUSES:
            return jsonify({
                "message": "Invalid report status"
            }), 400

        query = query.filter(
            Report.status == status
        )

    if report_type:
        query = query.filter(
            Report.report_type == report_type
        )

    reports = query.order_by(
        Report.submitted_at.desc()
    ).all()

    return jsonify([
        report.to_dict()
        for report in reports
    ]), 200


@reports_bp.route("/<int:report_id>", methods=["GET"])
def get_report(report_id):
    report = Report.query.get(report_id)

    if not report:
        return jsonify({
            "message": "Report not found"
        }), 404

    return jsonify(
        report.to_dict()
    ), 200


@reports_bp.route("/<int:report_id>/review", methods=["PUT"])
def review_report(report_id):
    report = Report.query.get(report_id)

    if not report:
        return jsonify({
            "message": "Report not found"
        }), 404

    data = request.get_json() or {}

    status = data.get("status")

    if not status:
        return jsonify({
            "message": "status is required"
        }), 400

    status = status.upper()

    if status not in VALID_STATUSES:
        return jsonify({
            "message": "Invalid report status"
        }), 400

    reviewed_by = data.get("reviewed_by")

    if reviewed_by:
        try:
            reviewed_by = int(reviewed_by)
        except (TypeError, ValueError):
            return jsonify({
                "message": "Invalid reviewed_by"
            }), 400

        reviewer = User.query.get(reviewed_by)

        if not reviewer:
            return jsonify({
                "message": "Reviewer not found"
            }), 404

        if reviewer.role.value not in {
            "ADMIN",
            "COORDINATOR",
            "ACADEMIC_SUPERVISOR"
        }:
            return jsonify({
                "message": "User is not allowed to review reports"
            }), 403

        if reviewer.status.value != "ACTIVE":
            return jsonify({
                "message": "Reviewer account is inactive"
            }), 403

    report.status = status
    report.feedback = data.get("feedback")
    report.reviewed_by = reviewed_by
    report.reviewed_at = datetime.utcnow()

    message = (
        f"Your report '{report.title or report.report_type}' "
        f"was {status.lower()}."
    )

    if report.feedback:
        message += f" Feedback: {report.feedback}"

    db.session.add(
        Notification(
            user_id=report.student_id,
            message=message,
            type="REPORT"
        )
    )

    db.session.commit()

    return jsonify({
        "message": "Report reviewed successfully",
        "report": report.to_dict()
    }), 200


@reports_bp.route("/<int:report_id>", methods=["PUT"])
def update_report(report_id):
    report = Report.query.get(report_id)

    if not report:
        return jsonify({
            "message": "Report not found"
        }), 404

    data = _get_input()

    if data.get("title") is not None:
        report.title = data.get("title")

    if data.get("description") is not None:
        report.description = data.get("description")

    if data.get("report_type") is not None:
        report.report_type = data.get("report_type")

    if request.files.get("file"):
        try:
            report.file_path = save_upload(
                request.files.get("file"),
                "reports"
            )
        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

    db.session.commit()

    return jsonify({
        "message": "Report updated successfully",
        "report": report.to_dict()
    }), 200


@reports_bp.route("/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    report = Report.query.get(report_id)

    if not report:
        return jsonify({
            "message": "Report not found"
        }), 404

    db.session.delete(report)
    db.session.commit()

    return jsonify({
        "message": "Report deleted successfully"
    }), 200


@reports_bp.route("/stats", methods=["GET"])
def report_stats():
    total = Report.query.count()

    pending = Report.query.filter(
        Report.status == "PENDING"
    ).count()

    under_review = Report.query.filter(
        Report.status == "UNDER_REVIEW"
    ).count()

    approved = Report.query.filter(
        Report.status == "APPROVED"
    ).count()

    rejected = Report.query.filter(
        Report.status == "REJECTED"
    ).count()

    return jsonify({
        "total": total,
        "pending": pending,
        "under_review": under_review,
        "approved": approved,
        "rejected": rejected
    }), 200