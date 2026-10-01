from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from database import db
from models import User


users_bp = Blueprint("users", __name__)

ADMIN_USERNAME = "Administration"


def normalize_role(role):
    allowed_roles = {
        "STUDENT",
        "FIELD_SUPERVISOR",
        "ACADEMIC_SUPERVISOR",
        "COORDINATOR",
        "ADMIN"
    }

    role = str(role or "STUDENT").strip().upper()

    if role not in allowed_roles:
        return None

    return role


def normalize_status(status):
    allowed_statuses = {
        "ACTIVE",
        "INACTIVE"
    }

    status = str(status or "ACTIVE").strip().upper()

    if status not in allowed_statuses:
        return None

    return status


def is_protected_admin(user):
    return user.institutional_id == ADMIN_USERNAME and user.role == "ADMIN"


@users_bp.route("/", methods=["GET"])
def get_users():
    query = User.query

    role = request.args.get("role")
    status = request.args.get("status")
    search = request.args.get("search")

    if role:
        role = normalize_role(role)

        if not role:
            return jsonify({"message": "Invalid role"}), 400

        query = query.filter(User.role == role)

    if status:
        status = normalize_status(status)

        if not status:
            return jsonify({"message": "Invalid status"}), 400

        query = query.filter(User.status == status)

    if search:
        search = search.strip()

        if search:
            like = f"%{search}%"

            query = query.filter(
                (User.name.ilike(like)) |
                (User.email.ilike(like)) |
                (User.institutional_id.ilike(like)) |
                (User.phone.ilike(like)) |
                (User.batch_number.ilike(like))
            )

    users = query.order_by(User.id.desc()).all()

    return jsonify([
        user.to_dict()
        for user in users
    ]), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify(user.to_dict()), 200


@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json() or {}

    institutional_id = str(
        data.get("institutional_id") or ""
    ).strip()

    name = str(
        data.get("name") or ""
    ).strip()

    email = str(
        data.get("email") or ""
    ).strip()

    phone = str(
        data.get("phone") or ""
    ).strip()

    programme = str(
        data.get("programme") or ""
    ).strip()

    batch_number = str(
        data.get("batch_number") or ""
    ).strip() or None

    password = data.get("password")

    role = normalize_role(
        data.get("role", "STUDENT")
    )

    status = normalize_status(
        data.get("status", "ACTIVE")
    )

    if not institutional_id or not name or not email or not password:
        return jsonify({
            "message": "institutional_id, name, email and password are required"
        }), 400

    if not role:
        return jsonify({
            "message": "Invalid role"
        }), 400

    if not status:
        return jsonify({
            "message": "Invalid status"
        }), 400

    if User.query.filter_by(
        institutional_id=institutional_id
    ).first():
        return jsonify({
            "message": "Institutional ID already registered"
        }), 409

    if User.query.filter_by(
        email=email
    ).first():
        return jsonify({
            "message": "Email already registered"
        }), 409

    new_user = User(
        institutional_id=institutional_id,
        name=name,
        email=email,
        phone=phone,
        programme=programme,
        batch_number=batch_number,
        password=generate_password_hash(password),
        role=role,
        status=status
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": new_user.to_dict()
    }), 201


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    data = request.get_json() or {}

    if "institutional_id" in data:
        institutional_id = str(
            data.get("institutional_id") or ""
        ).strip()

        if not institutional_id:
            return jsonify({
                "message": "Institutional ID cannot be empty"
            }), 400

        existing = User.query.filter(
            User.institutional_id == institutional_id,
            User.id != user_id
        ).first()

        if existing:
            return jsonify({
                "message": "Institutional ID already registered"
            }), 409

        if is_protected_admin(user):
            if institutional_id != ADMIN_USERNAME:
                return jsonify({
                    "message": "Administration username cannot be changed"
                }), 403

        user.institutional_id = institutional_id

    if "name" in data:
        user.name = str(
            data.get("name") or ""
        ).strip()

    if "email" in data:
        email = str(
            data.get("email") or ""
        ).strip()

        if not email:
            return jsonify({
                "message": "Email cannot be empty"
            }), 400

        existing = User.query.filter(
            User.email == email,
            User.id != user_id
        ).first()

        if existing:
            return jsonify({
                "message": "Email already registered"
            }), 409

        user.email = email

    if "phone" in data:
        user.phone = str(
            data.get("phone") or ""
        ).strip()

    if "programme" in data:
        user.programme = str(
            data.get("programme") or ""
        ).strip()

    if "batch_number" in data:
        user.batch_number = str(
            data.get("batch_number") or ""
        ).strip() or None

    if "role" in data:
        role = normalize_role(
            data.get("role")
        )

        if not role:
            return jsonify({
                "message": "Invalid role"
            }), 400

        if is_protected_admin(user) and role != "ADMIN":
            return jsonify({
                "message": "Administration role cannot be changed"
            }), 403

        user.role = role

    if "status" in data:
        status = normalize_status(
            data.get("status")
        )

        if not status:
            return jsonify({
                "message": "Invalid status"
            }), 400

        if is_protected_admin(user) and status != "ACTIVE":
            return jsonify({
                "message": "Administration account cannot be deactivated"
            }), 403

        user.status = status

    if data.get("password"):
        user.password = generate_password_hash(
            str(data["password"])
        )

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    }), 200


@users_bp.route("/<int:user_id>/status", methods=["PATCH"])
def toggle_user_status(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if is_protected_admin(user):
        return jsonify({
            "message": "Administration account cannot be deactivated"
        }), 403

    data = request.get_json() or {}

    new_status = data.get("status")

    if new_status:
        new_status = normalize_status(new_status)

        if not new_status:
            return jsonify({
                "message": "Invalid status"
            }), 400
    else:
        new_status = (
            "INACTIVE"
            if user.status == "ACTIVE"
            else "ACTIVE"
        )

    user.status = new_status

    db.session.commit()

    return jsonify({
        "message": "User status updated",
        "user": user.to_dict()
    }), 200


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if is_protected_admin(user):
        return jsonify({
            "message": "Administration account cannot be deleted"
        }), 403

    try:
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "message": "User deleted successfully"
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "message": (
                "User cannot be deleted because it is linked "
                "to other records. Deactivate the user instead."
            )
        }), 409


@users_bp.route("/stats", methods=["GET"])
def user_stats():
    total = User.query.count()

    students = User.query.filter_by(
        role="STUDENT"
    ).count()

    field_supervisors = User.query.filter_by(
        role="FIELD_SUPERVISOR"
    ).count()

    academic_supervisors = User.query.filter_by(
        role="ACADEMIC_SUPERVISOR"
    ).count()

    coordinators = User.query.filter_by(
        role="COORDINATOR"
    ).count()

    admins = User.query.filter_by(
        role="ADMIN"
    ).count()

    active = User.query.filter_by(
        status="ACTIVE"
    ).count()

    return jsonify({
        "total": total,
        "students": students,
        "field_supervisors": field_supervisors,
        "academic_supervisors": academic_supervisors,
        "coordinators": coordinators,
        "admins": admins,
        "active": active,
        "supervisors": (
            field_supervisors +
            academic_supervisors
        )
    }), 200