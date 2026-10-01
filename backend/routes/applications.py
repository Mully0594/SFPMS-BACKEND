import random
import string
from datetime import datetime

from flask import Blueprint, request, jsonify

from database import db
from models import (
    Application,
    User,
    Organization,
    Placement,
    Notification
)

from email_service import send_approval_email

try:
    from utils.uploads import save_upload
except ImportError:
    try:
        from uploads import save_upload
    except ImportError:
        save_upload = None


applications_bp = Blueprint(
    "applications",
    __name__
)


VALID_STATUSES = {
    "PENDING",
    "UNDER_REVIEW",
    "APPROVED",
    "REJECTED"
}


def _generate_app_code():
    while True:
        code = "APP" + "".join(
            random.choices(
                string.digits,
                k=6
            )
        )

        existing = Application.query.filter_by(
            application_code=code
        ).first()

        if not existing:
            return code


def _generate_batch_number():
    year = datetime.utcnow().year
    prefix = f"{str(year)[-2:]}eGAZ"

    users = (
        User.query
        .filter(
            User.batch_number.isnot(None),
            User.batch_number.like(f"{prefix}%")
        )
        .order_by(User.id.desc())
        .all()
    )

    highest = 0

    for user in users:
        try:
            number = int(user.batch_number[-3:])

            if number > highest:
                highest = number

        except (ValueError, TypeError):
            continue

    next_number = highest + 1

    while True:
        batch_number = f"{prefix}{next_number:03d}"

        existing = User.query.filter_by(
            batch_number=batch_number
        ).first()

        if not existing:
            return batch_number

        next_number += 1


def _parse_date(value):
    if not value:
        return None

    if hasattr(value, "year"):
        return value

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return None


def _get_input(data, key, default=""):
    value = data.get(key)

    if value is None:
        return default

    if isinstance(value, str):
        return value.strip()

    return value


def _get_active_placement(student_id):
    return (
        Placement.query
        .filter_by(student_id=student_id)
        .order_by(Placement.id.desc())
        .first()
    )


def _get_student(student_id):
    try:
        student_id = int(student_id)
    except (TypeError, ValueError):
        return None

    return User.query.get(student_id)


def _create_notification(
    student_id,
    title,
    message
):
    try:
        notification = Notification(
            user_id=student_id,
            title=title,
            message=message
        )

        db.session.add(notification)

        return notification

    except TypeError:
        try:
            notification = Notification(
                recipient_id=student_id,
                title=title,
                message=message
            )

            db.session.add(notification)

            return notification

        except Exception:
            return None

    except Exception:
        return None


@applications_bp.route("/", methods=["POST"])
def create_application():

    data = request.form.to_dict()

    if not data:
        data = request.get_json(silent=True) or {}

    student_id = (
        data.get("student_id")
        or data.get("user_id")
    )

    if not student_id:
        return jsonify({
            "message": "Student ID is required"
        }), 400

    student = _get_student(student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    if student.role != "STUDENT":
        return jsonify({
            "message": "Only students can submit applications"
        }), 403

    if student.batch_number:
        return jsonify({
            "message": (
                "Your application has already been approved "
                "and you already have a Batch Number."
            ),
            "batch_number": student.batch_number
        }), 409

    existing = (
        Application.query
        .filter_by(student_id=student.id)
        .order_by(Application.id.desc())
        .first()
    )

    if existing:
        if existing.status in {
            "PENDING",
            "UNDER_REVIEW",
            "APPROVED"
        }:
            return jsonify({
                "message": (
                    "You have already submitted an application."
                ),
                "application": existing.to_dict()
            }), 409

    organization_id = data.get(
        "organization_id"
    )

    preferred_organization = _get_input(
        data,
        "preferred_organization"
    )

    organization = None

    if organization_id:
        try:
            organization = Organization.query.get(
                int(organization_id)
            )
        except (TypeError, ValueError):
            organization = None

        if not organization:
            return jsonify({
                "message": "Organization not found"
            }), 404

        if hasattr(organization, "status"):
            if organization.status != "ACTIVE":
                return jsonify({
                    "message": "Selected organization is inactive"
                }), 400

    elif preferred_organization:
        organization = (
            Organization.query
            .filter(
                db.func.lower(
                    Organization.name
                ) == preferred_organization.lower()
            )
            .first()
        )

    application = Application(
        application_code=_generate_app_code(),
        student_id=student.id,

        first_name=_get_input(
            data,
            "first_name"
        ),

        middle_name=_get_input(
            data,
            "middle_name"
        ),

        last_name=_get_input(
            data,
            "last_name"
        ),

        gender=_get_input(
            data,
            "gender"
        ),

        date_of_birth=_parse_date(
            data.get("date_of_birth")
        ),

        nationality=_get_input(
            data,
            "nationality"
        ),

        national_id=_get_input(
            data,
            "national_id"
        ),

        phone=_get_input(
            data,
            "phone"
        ) or student.phone,

        email=_get_input(
            data,
            "email"
        ) or student.email,

        alternative_phone=_get_input(
            data,
            "alternative_phone"
        ),

        address=_get_input(
            data,
            "address"
        ),

        region=_get_input(
            data,
            "region"
        ),

        district=_get_input(
            data,
            "district"
        ),

        ward=_get_input(
            data,
            "ward"
        ),

        student_number=_get_input(
            data,
            "student_number"
        ) or student.institutional_id,

        programme=_get_input(
            data,
            "programme"
        ) or student.programme,

        department=_get_input(
            data,
            "department"
        ),

        year_of_study=_get_input(
            data,
            "year_of_study"
        ),

        academic_year=_get_input(
            data,
            "academic_year"
        ),

        institution=_get_input(
            data,
            "institution"
        ),

        organization_id=(
            organization.id
            if organization
            else None
        ),

        preferred_organization=(
            preferred_organization
            or (
                organization.name
                if organization
                else None
            )
        ),

        organization_type=_get_input(
            data,
            "organization_type"
        ),

        preferred_location=_get_input(
            data,
            "preferred_location"
        ),

        placement_start_date=_parse_date(
            data.get("placement_start_date")
        ),

        placement_end_date=_parse_date(
            data.get("placement_end_date")
        ),

        placement_duration=_get_input(
            data,
            "placement_duration"
        ),

        preferred_department=_get_input(
            data,
            "preferred_department"
        ),

        skills=_get_input(
            data,
            "skills"
        ),

        placement_reason=_get_input(
            data,
            "placement_reason"
        ),

        status="PENDING"
    )

    db.session.add(application)

    db.session.flush()

    if save_upload:
        try:
            application_letter = request.files.get(
                "application_letter"
            )

            if application_letter:
                application.application_letter_path = (
                    save_upload(
                        application_letter,
                        "applications"
                    )
                )

            cv = request.files.get("cv")

            if cv:
                application.cv_path = save_upload(
                    cv,
                    "applications"
                )

            student_id_copy = request.files.get(
                "student_id_copy"
            )

            if student_id_copy:
                application.student_id_copy_path = (
                    save_upload(
                        student_id_copy,
                        "applications"
                    )
                )

        except Exception:
            pass

    _create_notification(
        student.id,
        "Application Submitted",
        (
            "Your field placement application has "
            "been submitted successfully and is "
            "waiting for review."
        )
    )

    db.session.commit()

    return jsonify({
        "message": "Application submitted successfully",
        "application": application.to_dict()
    }), 201


@applications_bp.route("/", methods=["GET"])
def get_applications():

    student_id = request.args.get(
        "student_id"
    )

    status = request.args.get(
        "status"
    )

    search = request.args.get(
        "search"
    )

    query = Application.query

    if student_id:
        try:
            query = query.filter(
                Application.student_id == int(student_id)
            )
        except ValueError:
            return jsonify({
                "message": "Invalid student ID"
            }), 400

    if status:
        query = query.filter(
            Application.status == status.upper()
        )

    if search:
        search_value = f"%{search.strip()}%"

        query = query.filter(
            db.or_(
                Application.application_code.ilike(
                    search_value
                ),
                Application.first_name.ilike(
                    search_value
                ),
                Application.middle_name.ilike(
                    search_value
                ),
                Application.last_name.ilike(
                    search_value
                ),
                Application.email.ilike(
                    search_value
                ),
                Application.student_number.ilike(
                    search_value
                )
            )
        )

    applications = (
        query
        .order_by(
            Application.id.desc()
        )
        .all()
    )

    return jsonify([
        application.to_dict()
        for application in applications
    ]), 200


@applications_bp.route(
    "/<int:application_id>",
    methods=["GET"]
)
def get_application(application_id):

    application = Application.query.get(
        application_id
    )

    if not application:
        return jsonify({
            "message": "Application not found"
        }), 404

    return jsonify(
        application.to_dict()
    ), 200


@applications_bp.route(
    "/<int:application_id>/status",
    methods=["PUT"]
)
def update_application_status(
    application_id
):

    application = Application.query.get(
        application_id
    )

    if not application:
        return jsonify({
            "message": "Application not found"
        }), 404

    data = request.get_json() or {}

    new_status = (
        data.get("status")
        or ""
    ).strip().upper()

    if new_status not in VALID_STATUSES:
        return jsonify({
            "message": (
                "Invalid status. Use PENDING, "
                "UNDER_REVIEW, APPROVED or REJECTED."
            )
        }), 400

    rejection_reason = (
        data.get("rejection_reason")
        or data.get("reason")
        or ""
    ).strip()

    reviewed_by = data.get(
        "reviewed_by"
    )

    if reviewed_by:
        try:
            application.reviewed_by = int(
                reviewed_by
            )
        except (TypeError, ValueError):
            pass

    application.status = new_status
    application.reviewed_at = datetime.utcnow()

    if new_status == "REJECTED":
        application.rejection_reason = (
            rejection_reason or None
        )
    else:
        application.rejection_reason = None

    student = User.query.get(
        application.student_id
    )

    if not student:
        return jsonify({
            "message": "Student account not found"
        }), 404

    batch_number = None

    if new_status == "APPROVED":

        if not application.organization_id:
            return jsonify({
                "message": (
                    "Application has no organization. "
                    "Please assign an organization before approval."
                )
            }), 400

        organization = Organization.query.get(
            application.organization_id
        )

        if not organization:
            return jsonify({
                "message": "Organization not found"
            }), 404

        if hasattr(organization, "status"):
            if organization.status != "ACTIVE":
                return jsonify({
                    "message": "Organization is inactive"
                }), 400

        if not student.batch_number:
            student.batch_number = (
                _generate_batch_number()
            )

        batch_number = student.batch_number

        placement = (
            Placement.query
            .filter_by(
                student_id=student.id
            )
            .first()
        )

        if placement:

            if hasattr(
                placement,
                "organization_id"
            ):
                placement.organization_id = (
                    organization.id
                )

            if hasattr(
                placement,
                "application_id"
            ):
                placement.application_id = (
                    application.id
                )

            if hasattr(
                placement,
                "start_date"
            ):
                placement.start_date = (
                    application.placement_start_date
                )

            if hasattr(
                placement,
                "end_date"
            ):
                placement.end_date = (
                    application.placement_end_date
                )

            if hasattr(
                placement,
                "status"
            ):
                placement.status = "ACTIVE"

        else:

            placement_data = {
                "student_id": student.id
            }

            if hasattr(
                Placement,
                "application_id"
            ):
                placement_data[
                    "application_id"
                ] = application.id

            if hasattr(
                Placement,
                "organization_id"
            ):
                placement_data[
                    "organization_id"
                ] = organization.id

            if hasattr(
                Placement,
                "start_date"
            ):
                placement_data[
                    "start_date"
                ] = application.placement_start_date

            if hasattr(
                Placement,
                "end_date"
            ):
                placement_data[
                    "end_date"
                ] = application.placement_end_date

            if hasattr(
                Placement,
                "status"
            ):
                placement_data[
                    "status"
                ] = "ACTIVE"

            try:
                placement = Placement(
                    **placement_data
                )

                db.session.add(placement)

            except TypeError:

                placement_data = {
                    "student_id": student.id,
                    "organization_id": organization.id
                }

                try:
                    placement = Placement(
                        **placement_data
                    )

                    db.session.add(placement)

                except Exception:
                    pass

        _create_notification(
            student.id,
            "Application Approved",
            (
                "Your field placement application "
                "has been approved. Your Batch Number "
                f"is {batch_number}. Please logout and "
                "login again using your Batch Number "
                "and your existing password."
            )
        )

    elif new_status == "REJECTED":

        _create_notification(
            student.id,
            "Application Rejected",
            (
                "Your field placement application "
                "has been rejected."
                + (
                    f" Reason: {rejection_reason}"
                    if rejection_reason
                    else ""
                )
            )
        )

    elif new_status == "UNDER_REVIEW":

        _create_notification(
            student.id,
            "Application Under Review",
            (
                "Your field placement application "
                "is currently under review."
            )
        )

    elif new_status == "PENDING":

        _create_notification(
            student.id,
            "Application Pending",
            (
                "Your field placement application "
                "is pending review."
            )
        )

    db.session.commit()

    if new_status == "APPROVED" and batch_number and student.email:
        try:
            send_approval_email(
                student.email,
                student.name,
                batch_number
            )
        except Exception as email_error:
            print(
                f"Approval email failed for {student.email}: "
                f"{email_error}"
            )

    response = {
        "message": (
            "Application status updated successfully"
        ),
        "application": application.to_dict(),
        "status": application.status
    }

    if batch_number:
        response["batch_number"] = batch_number
        response["login_type"] = "BATCH"
        response["access_level"] = "FULL_STUDENT"

    return jsonify(response), 200


@applications_bp.route(
    "/<int:application_id>",
    methods=["DELETE"]
)
def delete_application(application_id):

    application = Application.query.get(
        application_id
    )

    if not application:
        return jsonify({
            "message": "Application not found"
        }), 404

    placement = (
        Placement.query
        .filter_by(
            student_id=application.student_id
        )
        .first()
    )

    if placement:
        return jsonify({
            "message": (
                "This application cannot be deleted "
                "because a placement already exists."
            )
        }), 409

    db.session.delete(application)

    db.session.commit()

    return jsonify({
        "message": "Application deleted successfully"
    }), 200


@applications_bp.route(
    "/stats",
    methods=["GET"]
)
def application_stats():

    total = Application.query.count()

    pending = (
        Application.query
        .filter_by(status="PENDING")
        .count()
    )

    under_review = (
        Application.query
        .filter_by(status="UNDER_REVIEW")
        .count()
    )

    approved = (
        Application.query
        .filter_by(status="APPROVED")
        .count()
    )

    rejected = (
        Application.query
        .filter_by(status="REJECTED")
        .count()
    )

    return jsonify({
        "total": total,
        "pending": pending,
        "under_review": under_review,
        "approved": approved,
        "rejected": rejected
    }), 200