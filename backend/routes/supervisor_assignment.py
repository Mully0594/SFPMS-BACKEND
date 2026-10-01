from flask import Blueprint, request, jsonify

from database import db
from models import supervisor_assignment, User, Notification


supervisor_assignment_bp = Blueprint(
    "supervisor_assignment",
    __name__
)


VALID_ROLES = {
    "FIELD_SUPERVISOR",
    "ACADEMIC_SUPERVISOR"
}


def _role_value(role):
    if hasattr(role, "value"):
        return role.value

    return str(role or "").strip().upper()


def _normalize_role(role):
    role = _role_value(role)

    if role not in VALID_ROLES:
        return None

    return role


def _assignment_exists(
    student_id,
    supervisor_id,
    role=None,
    exclude_id=None
):
    query = supervisor_assignment.query.filter(
        supervisor_assignment.student_id == student_id,
        supervisor_assignment.supervisor_id == supervisor_id
    )

    if role:
        query = query.filter(
            supervisor_assignment.role == role
        )

    if exclude_id:
        query = query.filter(
            supervisor_assignment.id != exclude_id
        )

    return query.first()


def _student_dict(student):
    if not student:
        return None

    return {
        "id": student.id,
        "institutional_id": student.institutional_id,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "programme": student.programme,
        "batch_number": student.batch_number,
        "role": _role_value(student.role),
        "status": _role_value(student.status),
        "created_at": (
            str(student.created_at)
            if student.created_at
            else None
        ),
        "updated_at": (
            str(student.updated_at)
            if student.updated_at
            else None
        )
    }


def _supervisor_dict(supervisor):
    if not supervisor:
        return None

    return {
        "id": supervisor.id,
        "institutional_id": supervisor.institutional_id,
        "name": supervisor.name,
        "email": supervisor.email,
        "phone": supervisor.phone,
        "programme": supervisor.programme,
        "role": _role_value(supervisor.role),
        "status": _role_value(supervisor.status)
    }


def _assignment_dict(assignment):
    return {
        "id": assignment.id,
        "student_id": assignment.student_id,
        "supervisor_id": assignment.supervisor_id,
        "role": _role_value(assignment.role),
        "assigned_at": (
            str(assignment.assigned_at)
            if assignment.assigned_at
            else None
        )
    }


@supervisor_assignment_bp.route(
    "/",
    methods=["POST"]
)
def create_supervisor_assignment():

    data = request.get_json() or {}

    student_id = data.get("student_id")
    supervisor_id = data.get("supervisor_id")
    requested_role = data.get("role")

    if not student_id or not supervisor_id:
        return jsonify({
            "message": "student_id and supervisor_id are required"
        }), 400

    try:
        student_id = int(student_id)
        supervisor_id = int(supervisor_id)
    except (TypeError, ValueError):
        return jsonify({
            "message": (
                "student_id and supervisor_id "
                "must be valid numbers"
            )
        }), 400

    student = User.query.get(student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    if _role_value(student.role) != "STUDENT":
        return jsonify({
            "message": "student_id must belong to a student"
        }), 400

    if _role_value(student.status) != "ACTIVE":
        return jsonify({
            "message": "Student account is inactive"
        }), 400

    supervisor = User.query.get(supervisor_id)

    if not supervisor:
        return jsonify({
            "message": "Supervisor not found"
        }), 404

    supervisor_role = _role_value(supervisor.role)

    if supervisor_role not in VALID_ROLES:
        return jsonify({
            "message": "User is not a valid supervisor"
        }), 400

    if _role_value(supervisor.status) != "ACTIVE":
        return jsonify({
            "message": "Supervisor account is inactive"
        }), 400

    role = _normalize_role(
        requested_role or supervisor_role
    )

    if not role:
        return jsonify({
            "message": "Invalid supervisor role"
        }), 400

    if role != supervisor_role:
        return jsonify({
            "message": (
                "Assignment role must match "
                "the supervisor's current role"
            )
        }), 400

    existing = _assignment_exists(
        student_id,
        supervisor_id,
        role
    )

    if existing:
        return jsonify({
            "message": (
                "This supervisor is already assigned "
                "to this student"
            )
        }), 409

    assignment = supervisor_assignment(
        student_id=student_id,
        supervisor_id=supervisor_id,
        role=role
    )

    db.session.add(assignment)

    supervisor_title = (
        "Field Supervisor"
        if role == "FIELD_SUPERVISOR"
        else "Academic Supervisor"
    )

    db.session.add(
        Notification(
            user_id=student_id,
            message=(
                f"{supervisor.name} has been assigned "
                f"as your {supervisor_title}."
            ),
            type="SUPERVISOR"
        )
    )

    db.session.commit()

    return jsonify({
        "message": "Supervisor assigned successfully",
        "assignment": _assignment_dict(assignment),
        "student": _student_dict(student),
        "supervisor": _supervisor_dict(supervisor)
    }), 201


@supervisor_assignment_bp.route(
    "/",
    methods=["GET"]
)
def get_supervisor_assignments():

    query = supervisor_assignment.query

    student_id = request.args.get("student_id")
    supervisor_id = request.args.get("supervisor_id")
    role = request.args.get("role")

    if student_id:
        try:
            student_id = int(student_id)
        except (TypeError, ValueError):
            return jsonify({
                "message": "Invalid student_id"
            }), 400

        query = query.filter(
            supervisor_assignment.student_id == student_id
        )

    if supervisor_id:
        try:
            supervisor_id = int(supervisor_id)
        except (TypeError, ValueError):
            return jsonify({
                "message": "Invalid supervisor_id"
            }), 400

        query = query.filter(
            supervisor_assignment.supervisor_id == supervisor_id
        )

    if role:
        role = _normalize_role(role)

        if not role:
            return jsonify({
                "message": "Invalid supervisor role"
            }), 400

        query = query.filter(
            supervisor_assignment.role == role
        )

    assignments = query.order_by(
        supervisor_assignment.id.desc()
    ).all()

    result = []

    for assignment in assignments:

        student = User.query.get(
            assignment.student_id
        )

        supervisor = User.query.get(
            assignment.supervisor_id
        )

        result.append({
            "assignment": _assignment_dict(
                assignment
            ),
            "student": _student_dict(
                student
            ),
            "supervisor": _supervisor_dict(
                supervisor
            )
        })

    return jsonify(result), 200


@supervisor_assignment_bp.route(
    "/<int:assignment_id>",
    methods=["GET"]
)
def get_assignment(assignment_id):

    assignment = supervisor_assignment.query.get(
        assignment_id
    )

    if not assignment:
        return jsonify({
            "message": "Assignment not found"
        }), 404

    student = User.query.get(
        assignment.student_id
    )

    supervisor = User.query.get(
        assignment.supervisor_id
    )

    return jsonify({
        "assignment": _assignment_dict(
            assignment
        ),
        "student": _student_dict(
            student
        ),
        "supervisor": _supervisor_dict(
            supervisor
        )
    }), 200


@supervisor_assignment_bp.route(
    "/<int:assignment_id>",
    methods=["PUT"]
)
def update_supervisor_assignment(assignment_id):

    assignment = supervisor_assignment.query.get(
        assignment_id
    )

    if not assignment:
        return jsonify({
            "message": "Assignment not found"
        }), 404

    data = request.get_json() or {}

    student_id = data.get(
        "student_id",
        assignment.student_id
    )

    supervisor_id = data.get(
        "supervisor_id",
        assignment.supervisor_id
    )

    try:
        student_id = int(student_id)
        supervisor_id = int(supervisor_id)
    except (TypeError, ValueError):
        return jsonify({
            "message": (
                "student_id and supervisor_id "
                "must be valid numbers"
            )
        }), 400

    student = User.query.get(student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    if _role_value(student.role) != "STUDENT":
        return jsonify({
            "message": "Selected user is not a student"
        }), 400

    if _role_value(student.status) != "ACTIVE":
        return jsonify({
            "message": "Student account is inactive"
        }), 400

    supervisor = User.query.get(supervisor_id)

    if not supervisor:
        return jsonify({
            "message": "Supervisor not found"
        }), 404

    supervisor_role = _role_value(
        supervisor.role
    )

    if supervisor_role not in VALID_ROLES:
        return jsonify({
            "message": (
                "Selected user is not a valid supervisor"
            )
        }), 400

    if _role_value(supervisor.status) != "ACTIVE":
        return jsonify({
            "message": "Supervisor account is inactive"
        }), 400

    role = _normalize_role(
        data.get(
            "role",
            supervisor_role
        )
    )

    if not role:
        return jsonify({
            "message": "Invalid supervisor role"
        }), 400

    if role != supervisor_role:
        return jsonify({
            "message": (
                "Assignment role must match "
                "the supervisor's current role"
            )
        }), 400

    existing = _assignment_exists(
        student_id,
        supervisor_id,
        role,
        exclude_id=assignment_id
    )

    if existing:
        return jsonify({
            "message": (
                "This supervisor is already assigned "
                "to this student"
            )
        }), 409

    old_student_id = assignment.student_id

    assignment.student_id = student_id
    assignment.supervisor_id = supervisor_id
    assignment.role = role

    if old_student_id != student_id:

        db.session.add(
            Notification(
                user_id=old_student_id,
                message=(
                    "Your supervisor assignment "
                    "has been updated."
                ),
                type="SUPERVISOR"
            )
        )

    supervisor_title = (
        "Field Supervisor"
        if role == "FIELD_SUPERVISOR"
        else "Academic Supervisor"
    )

    db.session.add(
        Notification(
            user_id=student_id,
            message=(
                f"{supervisor.name} has been assigned "
                f"to you as your {supervisor_title}."
            ),
            type="SUPERVISOR"
        )
    )

    db.session.commit()

    return jsonify({
        "message": (
            "Supervisor assignment "
            "updated successfully"
        ),
        "assignment": _assignment_dict(
            assignment
        ),
        "student": _student_dict(
            student
        ),
        "supervisor": _supervisor_dict(
            supervisor
        )
    }), 200


@supervisor_assignment_bp.route(
    "/<int:assignment_id>",
    methods=["DELETE"]
)
def delete_supervisor_assignment(assignment_id):

    assignment = supervisor_assignment.query.get(
        assignment_id
    )

    if not assignment:
        return jsonify({
            "message": "Assignment not found"
        }), 404

    student_id = assignment.student_id

    role_name = (
        "Field Supervisor"
        if _role_value(assignment.role)
        == "FIELD_SUPERVISOR"
        else "Academic Supervisor"
    )

    db.session.add(
        Notification(
            user_id=student_id,
            message=(
                f"Your {role_name} assignment "
                "has been removed."
            ),
            type="SUPERVISOR"
        )
    )

    db.session.delete(assignment)

    db.session.commit()

    return jsonify({
        "message": "Assignment removed successfully"
    }), 200


@supervisor_assignment_bp.route(
    "/student/<int:student_id>",
    methods=["GET"]
)
def get_student_supervisors(student_id):

    student = User.query.get(student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    assignments = supervisor_assignment.query.filter_by(
        student_id=student_id
    ).order_by(
        supervisor_assignment.id.desc()
    ).all()

    result = []

    for assignment in assignments:

        supervisor = User.query.get(
            assignment.supervisor_id
        )

        result.append({
            "assignment": _assignment_dict(
                assignment
            ),
            "supervisor": _supervisor_dict(
                supervisor
            )
        })

    return jsonify(result), 200


@supervisor_assignment_bp.route(
    "/supervisor/<int:supervisor_id>",
    methods=["GET"]
)
def get_supervisor_students(supervisor_id):

    supervisor = User.query.get(
        supervisor_id
    )

    if not supervisor:
        return jsonify({
            "message": "Supervisor not found"
        }), 404

    supervisor_role = _role_value(
        supervisor.role
    )

    if supervisor_role not in VALID_ROLES:
        return jsonify({
            "message": "User is not a valid supervisor"
        }), 400

    assignments = supervisor_assignment.query.filter_by(
        supervisor_id=supervisor_id,
        role=supervisor_role
    ).order_by(
        supervisor_assignment.id.desc()
    ).all()

    result = []

    for assignment in assignments:

        student = User.query.get(
            assignment.student_id
        )

        if not student:
            continue

        result.append({
            "assignment": _assignment_dict(
                assignment
            ),
            "student": _student_dict(
                student
            ),
            "supervisor": _supervisor_dict(
                supervisor
            )
        })

    return jsonify(result), 200