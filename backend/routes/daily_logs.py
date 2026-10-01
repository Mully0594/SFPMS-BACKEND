import os
from datetime import datetime, timedelta, time

from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    current_app
)

from database import db

from models import (
    DailyLog,
    Placement,
    User,
    Organization,
    WeeklySummary
)


daily_logs_bp = Blueprint(
    "daily_logs",
    __name__
)


def get_upload_folder():
    folder = os.path.join(
        current_app.root_path,
        "uploads",
        "daily_logs"
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


def parse_time(value):
    if not value:
        return None

    formats = [
        "%H:%M:%S",
        "%H:%M",
        "%I:%M:%S %p",
        "%I:%M %p"
    ]

    for time_format in formats:
        try:
            return datetime.strptime(
                str(value).strip(),
                time_format
            ).time()
        except ValueError:
            continue

    raise ValueError(
        "Invalid time format"
    )


def get_now():
    return datetime.now()


def get_current_date():
    return get_now().date()


def get_current_time():
    return get_now().time()


def is_after_six_pm():
    return get_current_time() >= time(
        18,
        0,
        0
    )


def get_submission_date():
    current = get_now()

    if current.time() >= time(
        18,
        0,
        0
    ):
        return (
            current.date()
            + timedelta(days=1)
        )

    return current.date()


def get_submission_cycle_start():
    current = get_now()

    six_pm = current.replace(
        hour=18,
        minute=0,
        second=0,
        microsecond=0
    )

    if current >= six_pm:
        return six_pm

    previous_day = current - timedelta(
        days=1
    )

    return previous_day.replace(
        hour=18,
        minute=0,
        second=0,
        microsecond=0
    )


def seconds_until_six_pm():
    current = get_now()

    target = current.replace(
        hour=18,
        minute=0,
        second=0,
        microsecond=0
    )

    if current >= target:
        return 0

    return max(
        0,
        int(
            (
                target - current
            ).total_seconds()
        )
    )


def get_week_start(
    submission_date
):
    return (
        submission_date
        - timedelta(
            days=submission_date.weekday()
        )
    )


def get_week_end(
    submission_date
):
    return (
        get_week_start(
            submission_date
        )
        + timedelta(days=6)
    )


def log_to_dict(log):
    student = User.query.get(
        log.student_id
    )

    placement = Placement.query.get(
        log.placement_id
    )

    organization_name = None

    if (
        placement
        and placement.organization_id
    ):
        organization = Organization.query.get(
            placement.organization_id
        )

        if organization:
            organization_name = (
                organization.name
            )

    return {
        "id": log.id,

        "student_id": log.student_id,

        "student_name": (
            student.name
            if student
            else None
        ),

        "student_email": (
            student.email
            if student
            else None
        ),

        "institutional_id": (
            student.institutional_id
            if student
            else None
        ),

        "placement_id": log.placement_id,

        "organization_name": (
            organization_name
        ),

        "log_date": (
            str(log.log_date)
            if log.log_date
            else None
        ),

        "sign_in_time": (
            str(log.sign_in_time)
            if log.sign_in_time
            else None
        ),

        "sign_in_latitude": None,

        "sign_in_longitude": None,

        "sign_out_time": (
            str(log.sign_out_time)
            if log.sign_out_time
            else None
        ),

        "sign_out_latitude": None,

        "sign_out_longitude": None,

        "activity": (
            log.activity
            or ""
        ),

        "attachment": None,

        "attachment_url": None,

        "status": (
            log.status
            or "PENDING"
        )
    }


def weekly_summary_to_dict(
    summary
):
    if hasattr(
        summary,
        "to_dict"
    ):
        return summary.to_dict()

    return {
        "id": summary.id,

        "student_id": (
            summary.student_id
        ),

        "placement_id": (
            summary.placement_id
        ),

        "week_start": (
            str(summary.week_start)
            if summary.week_start
            else None
        ),

        "week_end": (
            str(summary.week_end)
            if summary.week_end
            else None
        ),

        "summary": (
            summary.summary
            or ""
        ),

        "status": (
            summary.status
            or "PENDING"
        ),

        "last_submitted_at": (
            summary.last_submitted_at.isoformat()
            if getattr(
                summary,
                "last_submitted_at",
                None
            )
            else None
        ),

        "created_at": (
            summary.created_at.isoformat()
            if getattr(
                summary,
                "created_at",
                None
            )
            else None
        ),

        "updated_at": (
            summary.updated_at.isoformat()
            if getattr(
                summary,
                "updated_at",
                None
            )
            else None
        )
    }


def get_current_weekly_summary(
    student_id,
    placement_id
):
    cycle_start = (
        get_submission_cycle_start()
    )

    summary = (
        WeeklySummary.query
        .filter(
            WeeklySummary.student_id
            == student_id
        )
        .filter(
            WeeklySummary.placement_id
            == placement_id
        )
        .filter(
            WeeklySummary.last_submitted_at
            >= cycle_start
        )
        .order_by(
            WeeklySummary.id.desc()
        )
        .first()
    )

    return summary


@daily_logs_bp.route(
    "/",
    methods=["POST"]
)
def create_daily_log():

    student_id = request.form.get(
        "student_id"
    )

    placement_id = request.form.get(
        "placement_id"
    )

    log_date = request.form.get(
        "log_date"
    )

    sign_in_time = request.form.get(
        "sign_in_time"
    )

    if (
        not student_id
        or not placement_id
        or not log_date
    ):
        return jsonify({
            "message": (
                "student_id, placement_id "
                "and log_date are required"
            )
        }), 400

    try:
        student_id = int(
            student_id
        )

        placement_id = int(
            placement_id
        )

    except (
        ValueError,
        TypeError
    ):
        return jsonify({
            "message": (
                "Invalid student_id "
                "or placement_id"
            )
        }), 400

    student = User.query.get(
        student_id
    )

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    if (
        str(
            student.role
        ).upper()
        != "STUDENT"
    ):
        return jsonify({
            "message": (
                "User is not a student"
            )
        }), 400

    placement = Placement.query.get(
        placement_id
    )

    if not placement:
        return jsonify({
            "message": "Placement not found"
        }), 404

    if (
        placement.student_id
        != student_id
    ):
        return jsonify({
            "message": (
                "This placement does not "
                "belong to this student"
            )
        }), 403

    if (
        str(
            placement.status
        ).upper()
        != "ACTIVE"
    ):
        return jsonify({
            "message": (
                "This placement is not active"
            )
        }), 400

    try:
        parsed_log_date = (
            datetime.strptime(
                log_date,
                "%Y-%m-%d"
            ).date()
        )

    except ValueError:
        return jsonify({
            "message": (
                "Invalid date format. "
                "Use YYYY-MM-DD"
            )
        }), 400

    submission_date = (
        get_submission_date()
    )

    if (
        parsed_log_date
        != submission_date
    ):
        return jsonify({
            "message": (
                "You can only submit "
                "the current submission day."
            ),
            "submission_date": str(
                submission_date
            ),
            "locked": True
        }), 400

    parsed_sign_in_time = None

    if sign_in_time:
        try:
            parsed_sign_in_time = (
                parse_time(
                    sign_in_time
                )
            )

        except ValueError:
            return jsonify({
                "message": (
                    "Invalid sign-in time"
                )
            }), 400

    existing_log = (
        DailyLog.query
        .filter_by(
            student_id=student_id,
            placement_id=placement_id,
            log_date=parsed_log_date
        )
        .order_by(
            DailyLog.id.desc()
        )
        .first()
    )

    if existing_log:
        return jsonify({
            "message": (
                "Attendance for this "
                "submission day already exists."
            ),
            "locked": True,
            "log": log_to_dict(
                existing_log
            ),
            "next_submission_after": (
                "18:00"
            )
        }), 409

    new_log = DailyLog(
        student_id=student_id,
        placement_id=placement_id,
        log_date=parsed_log_date,
        sign_in_time=parsed_sign_in_time,
        sign_in_latitude=None,
        sign_in_longitude=None,
        activity="",
        status="PENDING"
    )

    db.session.add(
        new_log
    )

    db.session.commit()

    return jsonify({
        "message": (
            "Signed in successfully"
        ),

        "log": log_to_dict(
            new_log
        ),

        "submission_date": str(
            submission_date
        ),

        "locked": False
    }), 201


@daily_logs_bp.route(
    "/<int:log_id>/sign-out",
    methods=["PUT"]
)
def sign_out(log_id):

    daily_log = DailyLog.query.get(
        log_id
    )

    if not daily_log:
        return jsonify({
            "message": (
                "Daily log not found"
            )
        }), 404

    if not daily_log.sign_in_time:
        return jsonify({
            "message": (
                "Student must sign in first"
            )
        }), 400

    if daily_log.sign_out_time:
        return jsonify({
            "message": (
                "Student has already "
                "signed out"
            ),
            "log": log_to_dict(
                daily_log
            )
        }), 409

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    sign_out_time = data.get(
        "sign_out_time"
    )

    try:
        parsed_sign_out_time = (
            parse_time(
                sign_out_time
            )
        )

    except (
        ValueError,
        AttributeError
    ):
        return jsonify({
            "message": (
                "Valid sign-out "
                "time is required"
            )
        }), 400

    daily_log.sign_out_time = (
        parsed_sign_out_time
    )

    daily_log.sign_out_latitude = None
    daily_log.sign_out_longitude = None

    db.session.commit()

    return jsonify({
        "message": (
            "Signed out successfully"
        ),

        "log": log_to_dict(
            daily_log
        )
    }), 200


@daily_logs_bp.route(
    "/<int:log_id>",
    methods=["PUT"]
)
def update_daily_log(log_id):

    daily_log = DailyLog.query.get(
        log_id
    )

    if not daily_log:
        return jsonify({
            "message": (
                "Daily log not found"
            )
        }), 404

    submission_date = (
        get_submission_date()
    )

    if (
        daily_log.log_date
        != submission_date
    ):
        return jsonify({
            "message": (
                "This daily log is "
                "closed and cannot "
                "be edited."
            ),
            "locked": True,
            "submission_date": str(
                submission_date
            )
        }), 403

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    activity = data.get(
        "activity"
    )

    if activity is not None:

        activity = str(
            activity
        ).strip()

        if not activity:
            return jsonify({
                "message": (
                    "Activity cannot "
                    "be empty"
                )
            }), 400

        if not daily_log.sign_in_time:
            return jsonify({
                "message": (
                    "Please sign in "
                    "before submitting "
                    "your activity."
                )
            }), 400

        if daily_log.activity:
            return jsonify({
                "message": (
                    "Today's daily "
                    "logbook has already "
                    "been submitted."
                ),

                "locked": True,

                "log": log_to_dict(
                    daily_log
                ),

                "next_submission_after": (
                    "18:00"
                )
            }), 409

        daily_log.activity = (
            activity
        )

    status = data.get(
        "status"
    )

    if status:
        daily_log.status = (
            str(
                status
            ).upper()
        )

    db.session.commit()

    return jsonify({
        "message": (
            "Daily activity "
            "submitted successfully"
        ),

        "log": log_to_dict(
            daily_log
        ),

        "locked": True,

        "next_submission_after": (
            "18:00"
        )
    }), 200


@daily_logs_bp.route(
    "/<int:log_id>",
    methods=["GET"]
)
def get_daily_log(log_id):

    daily_log = DailyLog.query.get(
        log_id
    )

    if not daily_log:
        return jsonify({
            "message": (
                "Daily log not found"
            )
        }), 404

    return jsonify(
        log_to_dict(
            daily_log
        )
    ), 200


@daily_logs_bp.route(
    "/",
    methods=["GET"]
)
def get_daily_logs():

    query = DailyLog.query

    student_id = request.args.get(
        "student_id"
    )

    placement_id = request.args.get(
        "placement_id"
    )

    status = request.args.get(
        "status"
    )

    if student_id:
        query = query.filter(
            DailyLog.student_id
            == student_id
        )

    if placement_id:
        query = query.filter(
            DailyLog.placement_id
            == placement_id
        )

    if status:
        query = query.filter(
            DailyLog.status
            == status.upper()
        )

    logs = (
        query
        .order_by(
            DailyLog.log_date.desc(),
            DailyLog.id.desc()
        )
        .all()
    )

    return jsonify([
        log_to_dict(
            log
        )
        for log in logs
    ]), 200


@daily_logs_bp.route(
    "/<int:log_id>/review",
    methods=["PUT"]
)
def review_daily_log(log_id):

    daily_log = DailyLog.query.get(
        log_id
    )

    if not daily_log:
        return jsonify({
            "message": (
                "Daily log not found"
            )
        }), 404

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    status = str(
        data.get(
            "status",
            ""
        )
    ).upper().strip()

    if status not in [
        "APPROVED",
        "REJECTED"
    ]:
        return jsonify({
            "message": (
                "Status must be APPROVED "
                "or REJECTED"
            )
        }), 400

    daily_log.status = status

    db.session.commit()

    return jsonify({
        "message": (
            f"Daily log "
            f"{status.lower()} successfully"
        ),

        "log": log_to_dict(
            daily_log
        )
    }), 200


@daily_logs_bp.route(
    "/weekly-summary",
    methods=["GET"]
)
def get_weekly_summary():

    student_id = request.args.get(
        "student_id"
    )

    placement_id = request.args.get(
        "placement_id"
    )

    if not student_id or not placement_id:
        return jsonify({
            "message": (
                "student_id and "
                "placement_id are required"
            )
        }), 400

    try:
        student_id = int(
            student_id
        )

        placement_id = int(
            placement_id
        )

    except (
        ValueError,
        TypeError
    ):
        return jsonify({
            "message": (
                "Invalid student_id "
                "or placement_id"
            )
        }), 400

    current_submission_date = (
        get_submission_date()
    )

    current_week_start = (
        get_week_start(
            current_submission_date
        )
    )

    summary = (
        get_current_weekly_summary(
            student_id,
            placement_id
        )
    )

    if not summary:
        return jsonify({
            "summary": None,
            "locked": False,
            "can_submit": True,
            "submission_date": str(
                current_submission_date
            ),
            "week_start": str(
                current_week_start
            ),
            "next_submission_after": None
        }), 200

    return jsonify({
        "summary": (
            weekly_summary_to_dict(
                summary
            )
        ),

        "locked": True,

        "can_submit": False,

        "submission_date": str(
            current_submission_date
        ),

        "week_start": str(
            current_week_start
        ),

        "next_submission_after": (
            "18:00"
        )
    }), 200


@daily_logs_bp.route(
    "/weekly-summary",
    methods=["POST"]
)
def save_weekly_summary():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    student_id = data.get(
        "student_id"
    )

    placement_id = data.get(
        "placement_id"
    )

    summary_text = str(
        data.get(
            "summary",
            ""
        )
    ).strip()

    if (
        not student_id
        or not placement_id
    ):
        return jsonify({
            "message": (
                "student_id and "
                "placement_id are required"
            )
        }), 400

    if not summary_text:
        return jsonify({
            "message": (
                "Weekly summary "
                "cannot be empty"
            )
        }), 400

    try:
        student_id = int(
            student_id
        )

        placement_id = int(
            placement_id
        )

    except (
        ValueError,
        TypeError
    ):
        return jsonify({
            "message": (
                "Invalid student_id "
                "or placement_id"
            )
        }), 400

    student = User.query.get(
        student_id
    )

    if not student:
        return jsonify({
            "message": (
                "Student not found"
            )
        }), 404

    if (
        str(
            student.role
        ).upper()
        != "STUDENT"
    ):
        return jsonify({
            "message": (
                "User is not a student"
            )
        }), 400

    placement = Placement.query.get(
        placement_id
    )

    if not placement:
        return jsonify({
            "message": (
                "Placement not found"
            )
        }), 404

    if (
        placement.student_id
        != student_id
    ):
        return jsonify({
            "message": (
                "This placement does not "
                "belong to this student"
            )
        }), 403

    if (
        str(
            placement.status
        ).upper()
        != "ACTIVE"
    ):
        return jsonify({
            "message": (
                "This placement is not active"
            )
        }), 400

    submission_date = (
        get_submission_date()
    )

    week_start = (
        get_week_start(
            submission_date
        )
    )

    week_end = (
        get_week_end(
            submission_date
        )
    )

    existing_summary = (
        get_current_weekly_summary(
            student_id,
            placement_id
        )
    )

    if existing_summary:
        return jsonify({
            "message": (
                "Weekly Summary has "
                "already been submitted "
                "for this cycle."
            ),

            "locked": True,

            "summary": (
                weekly_summary_to_dict(
                    existing_summary
                )
            ),

            "next_submission_after": (
                "18:00"
            )
        }), 409

    current_datetime = get_now()

    new_summary = WeeklySummary(
        student_id=student_id,
        placement_id=placement_id,
        week_start=week_start,
        week_end=week_end,
        summary=summary_text,
        status="PENDING"
    )

    if hasattr(
        new_summary,
        "last_submitted_at"
    ):
        new_summary.last_submitted_at = (
            current_datetime
        )

    db.session.add(
        new_summary
    )

    db.session.commit()

    return jsonify({
        "message": (
            "Weekly Summary "
            "submitted successfully"
        ),

        "summary": (
            weekly_summary_to_dict(
                new_summary
            )
        ),

        "locked": True,

        "can_submit": False,

        "submission_date": str(
            submission_date
        ),

        "next_submission_after": (
            "18:00"
        )
    }), 201


@daily_logs_bp.route(
    "/uploads/<path:filename>",
    methods=["GET"]
)
def download_daily_log_file(
    filename
):
    folder = get_upload_folder()

    return send_from_directory(
        folder,
        filename
    )