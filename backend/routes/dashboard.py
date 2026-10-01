from flask import Blueprint, jsonify

from models import (
    User,
    Organization,
    Application,
    Placement,
    DailyLog,
    Report,
    supervisor_assignment,
    FieldEvaluation,
    AcademicRemark,
)

dashboard_bp = Blueprint("dashboard", __name__)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@dashboard_bp.route("/admin", methods=["GET"])
def admin_dashboard():

    # -----------------------------------------------------
    # APPLICATION COUNTS
    # -----------------------------------------------------

    total_applications = Application.query.count()

    pending_applications = Application.query.filter(
        Application.status.in_([
            "PENDING",
            "UNDER REVIEW"
        ])
    ).count()

    approved_applications = Application.query.filter_by(
        status="APPROVED"
    ).count()

    rejected_applications = Application.query.filter_by(
        status="REJECTED"
    ).count()

    under_review_applications = Application.query.filter_by(
        status="UNDER REVIEW"
    ).count()

    applications_by_status = {
        "PENDING": Application.query.filter_by(
            status="PENDING"
        ).count(),

        "APPROVED": Application.query.filter_by(
            status="APPROVED"
        ).count(),

        "REJECTED": Application.query.filter_by(
            status="REJECTED"
        ).count(),
    }

    # -----------------------------------------------------
    # PLACEMENT COUNTS
    # -----------------------------------------------------

    active_placements = Placement.query.filter_by(
        status="ACTIVE"
    ).count()

    completed_placements = Placement.query.filter_by(
        status="COMPLETED"
    ).count()

    pending_placements = Placement.query.filter_by(
        status="PENDING"
    ).count()

    cancelled_placements = Placement.query.filter_by(
        status="CANCELLED"
    ).count()

    placements_by_status = {
        "ACTIVE": active_placements,
        "COMPLETED": completed_placements,
        "CANCELLED": cancelled_placements,
        "PENDING": pending_placements,
    }

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    total_users = User.query.count()

    total_students = User.query.filter_by(
        role="STUDENT"
    ).count()

    # -----------------------------------------------------
    # ORGANIZATIONS
    # -----------------------------------------------------

    total_organizations = Organization.query.count()

    active_organizations = Organization.query.filter_by(
        status="ACTIVE"
    ).count()

    # -----------------------------------------------------
    # SUPERVISORS
    # -----------------------------------------------------

    total_supervisors = User.query.filter(
        User.role.in_([
            "FIELD_SUPERVISOR",
            "ACADEMIC_SUPERVISOR"
        ])
    ).count()

    active_supervisors = User.query.filter(
        User.role.in_([
            "FIELD_SUPERVISOR",
            "ACADEMIC_SUPERVISOR"
        ]),
        User.status == "ACTIVE"
    ).count()

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return jsonify({

        # USERS
        "total_users": total_users,

        "total_students": total_students,

        # APPLICATIONS
        "total_applications": total_applications,

        "pending_applications": pending_applications,

        "approved_applications": approved_applications,

        "rejected_applications": rejected_applications,

        "under_review_applications": under_review_applications,

        "applications_by_status": {
            "PENDING": applications_by_status["PENDING"],
            "APPROVED": applications_by_status["APPROVED"],
            "REJECTED": applications_by_status["REJECTED"],
        },

        # PLACEMENTS
        "active_placements": active_placements,

        "completed_placements": completed_placements,

        "placements_by_status": {
            "ACTIVE": placements_by_status["ACTIVE"],
            "COMPLETED": placements_by_status["COMPLETED"],
            "CANCELLED": placements_by_status["CANCELLED"],
            "PENDING": placements_by_status["PENDING"],
        },

        # ORGANIZATIONS
        "total_organizations": total_organizations,

        "active_organizations": active_organizations,

        # SUPERVISORS
        "total_supervisors": total_supervisors,

        "active_supervisors": active_supervisors,

    }), 200


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@dashboard_bp.route("/student/<int:student_id>", methods=["GET"])
def student_dashboard(student_id):

    student = User.query.filter_by(
        id=student_id,
        role="STUDENT"
    ).first()

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    applications = (
        Application.query
        .filter_by(student_id=student_id)
        .order_by(Application.id.desc())
        .all()
    )

    latest_application = applications[0] if applications else None

    total_applications = len(applications)

    approved_applications = sum(
        1
        for application in applications
        if str(application.status).upper() == "APPROVED"
    )

    pending_applications = sum(
        1
        for application in applications
        if str(application.status).upper()
        in [
            "PENDING",
            "UNDER REVIEW"
        ]
    )

    rejected_applications = sum(
        1
        for application in applications
        if str(application.status).upper() == "REJECTED"
    )

    placements = (
        Placement.query
        .filter_by(student_id=student_id)
        .order_by(Placement.id.desc())
        .all()
    )

    active_placement = next(
        (
            placement
            for placement in placements
            if str(placement.status).upper() == "ACTIVE"
        ),
        None
    )

    logs = DailyLog.query.filter_by(
        student_id=student_id
    )

    total_logs = logs.count()

    approved_logs = logs.filter_by(
        status="APPROVED"
    ).count()

    pending_logs = logs.filter_by(
        status="PENDING"
    ).count()

    rejected_logs = logs.filter_by(
        status="REJECTED"
    ).count()

    present_days = logs.filter(
        DailyLog.sign_in_time.isnot(None)
    ).count()

    absent_days = logs.filter(
        DailyLog.sign_in_time.is_(None)
    ).count()

    reports = Report.query.filter_by(
        student_id=student_id
    )

    total_reports = reports.count()

    submitted_reports = reports.filter(
        Report.status.in_([
            "SUBMITTED",
            "APPROVED"
        ])
    ).count()

    pending_reports = reports.filter_by(
        status="PENDING"
    ).count()

    organization_name = ""

    if active_placement:

        organization_id = getattr(
            active_placement,
            "organization_id",
            None
        )

        if organization_id:

            organization = Organization.query.filter_by(
                id=organization_id
            ).first()

            if organization:
                organization_name = organization.name

    supervisor_name = ""

    if active_placement:

        field_supervisor_id = getattr(
            active_placement,
            "field_supervisor_id",
            None
        )

        if field_supervisor_id:

            supervisor = User.query.filter_by(
                id=field_supervisor_id
            ).first()

            if supervisor:
                supervisor_name = supervisor.name

    placement_status = "Not Assigned"

    if active_placement:
        placement_status = active_placement.status

    elif approved_applications > 0:
        placement_status = "Approved - Awaiting Placement"

    application_status = (
        latest_application.status
        if latest_application
        else None
    )

    application_submitted = (
        latest_application is not None
    )

    return jsonify({

        "student": student.to_dict(),

        "batch_number": student.batch_number,

        "application_status": application_status,

        "application_submitted": application_submitted,

        "total_applications": total_applications,

        "approved_applications": approved_applications,

        "pending_applications": pending_applications,

        "rejected_applications": rejected_applications,

        "total_attendance": total_logs,

        "present_days": present_days,

        "absent_days": absent_days,

        "total_logs": total_logs,

        "approved_logs": approved_logs,

        "pending_logs": pending_logs,

        "rejected_logs": rejected_logs,

        "total_reports": total_reports,

        "submitted_reports": submitted_reports,

        "pending_reports": pending_reports,

        "total_placements": len(placements),

        "placement_ids": [
            placement.id
            for placement in placements
        ],

        "placement_status": placement_status,

        "organization_name": organization_name,

        "supervisor_name": supervisor_name,

        "active_placement": (
            active_placement.to_dict()
            if active_placement
            else None
        ),

    }), 200


# =========================================================
# FIELD SUPERVISOR DASHBOARD
# =========================================================

@dashboard_bp.route(
    "/field-supervisor/<int:supervisor_id>",
    methods=["GET"]
)
def field_supervisor_dashboard(supervisor_id):

    assignments = supervisor_assignment.query.filter_by(
        supervisor_id=supervisor_id
    ).all()

    student_ids = list({
        assignment.student_id
        for assignment in assignments
    })

    pending_logs = (
        DailyLog.query.filter(
            DailyLog.student_id.in_(student_ids),
            DailyLog.status == "PENDING"
        ).count()
        if student_ids
        else 0
    )

    pending_evaluations = (
        len(student_ids)
        - FieldEvaluation.query.filter(
            FieldEvaluation.student_id.in_(student_ids),
            FieldEvaluation.supervisor_id == supervisor_id
        ).count()
        if student_ids
        else 0
    )

    return jsonify({

        "assigned_students": len(student_ids),

        "pending_logs": pending_logs,

        "pending_evaluations": max(
            pending_evaluations,
            0
        ),

        "student_ids": student_ids,

    }), 200


# =========================================================
# ACADEMIC SUPERVISOR DASHBOARD
# =========================================================

@dashboard_bp.route(
    "/academic-supervisor/<int:supervisor_id>",
    methods=["GET"]
)
def academic_supervisor_dashboard(supervisor_id):

    assignments = supervisor_assignment.query.filter_by(
        supervisor_id=supervisor_id
    ).all()

    student_ids = list({
        assignment.student_id
        for assignment in assignments
    })

    submitted_remarks = (
        AcademicRemark.query.filter(
            AcademicRemark.supervisor_id == supervisor_id,
            AcademicRemark.student_id.in_(student_ids),
            AcademicRemark.submitted.is_(True)
        ).count()
        if student_ids
        else 0
    )

    return jsonify({

        "assigned_students": len(student_ids),

        "submitted_remarks": submitted_remarks,

        "pending_remarks": max(
            len(student_ids) - submitted_remarks,
            0
        ),

        "student_ids": student_ids,

    }), 200