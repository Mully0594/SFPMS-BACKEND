from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import hashlib
from email_service import send_email

from database import db
from models import User
from models.password_reset_token import PasswordResetToken


auth_bp = Blueprint("auth", __name__)


ADMIN_USERNAME = "Administration"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Administration"


def ensure_admin_account():
    admin = User.query.filter_by(
        institutional_id=ADMIN_USERNAME
    ).first()

    if admin:
        admin.email = ADMIN_EMAIL
        admin.password = generate_password_hash(ADMIN_PASSWORD)
        admin.role = "ADMIN"
        admin.status = "ACTIVE"
        db.session.commit()
        return admin

    admin = User(
        institutional_id=ADMIN_USERNAME,
        name="Administration",
        email=ADMIN_EMAIL,
        phone="",
        programme="Administration",
        password=generate_password_hash(ADMIN_PASSWORD),
        role="ADMIN",
        status="ACTIVE",
        batch_number=None
    )

    db.session.add(admin)
    db.session.commit()

    return admin


def validate_password(password):
    if len(password) < 8:
        return False

    has_uppercase = any(
        char.isupper()
        for char in password
    )

    has_number = any(
        char.isdigit()
        for char in password
    )

    has_symbol = any(
        not char.isalnum()
        for char in password
    )

    return (
        has_uppercase
        and has_number
        and has_symbol
    )


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    institutional_id = (
        data.get("institutional_id")
        or ""
    ).strip()

    name = (
        data.get("name")
        or ""
    ).strip()

    email = (
        data.get("email")
        or ""
    ).strip().lower()

    phone = (
        data.get("phone")
        or ""
    ).strip()

    programme = (
        data.get("programme")
        or ""
    ).strip()

    password = data.get("password") or ""

    if (
        not institutional_id
        or not name
        or not email
        or not password
    ):
        return jsonify({
            "message": (
                "Institutional ID, name, email "
                "and password are required"
            )
        }), 400

    if not validate_password(password):
        return jsonify({
            "message": (
                "Password must contain at least "
                "8 characters, one capital letter, "
                "one number and one symbol"
            )
        }), 400

    existing_user = User.query.filter_by(
        institutional_id=institutional_id
    ).first()

    if existing_user:
        return jsonify({
            "message": "Institutional ID already registered"
        }), 409

    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email:
        return jsonify({
            "message": "Email already registered"
        }), 409

    new_user = User(
        institutional_id=institutional_id,
        name=name,
        email=email,
        phone=phone,
        programme=programme,
        password=generate_password_hash(password),
        role="STUDENT",
        status="ACTIVE",
        batch_number=None
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Student registered successfully",
        "user_id": new_user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    identifier = (
        data.get("identifier")
        or data.get("email")
        or data.get("institutional_id")
        or ""
    ).strip()

    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({
            "message": (
                "Email/Batch Number and password are required"
            )
        }), 400

    # =========================================================
    # ADMIN LOGIN
    # =========================================================

    if (
        identifier.lower() == ADMIN_EMAIL
        and password == ADMIN_PASSWORD
    ):
        admin = ensure_admin_account()

        return jsonify({
            "message": "Login successful",
            "login_type": "ADMIN",
            "access_level": "ADMIN",
            "user": admin.to_dict()
        }), 200

    # =========================================================
    # BATCH NUMBER LOGIN
    # =========================================================

    batch_user = User.query.filter_by(
        batch_number=identifier
    ).first()

    if batch_user:

        if batch_user.role != "STUDENT":
            return jsonify({
                "message": "Invalid login credentials"
            }), 401

        if batch_user.status != "ACTIVE":
            return jsonify({
                "message": "Your account is inactive"
            }), 403

        if not check_password_hash(
            batch_user.password,
            password
        ):
            return jsonify({
                "message": (
                    "Invalid Batch Number or password"
                )
            }), 401

        return jsonify({
            "message": "Login successful",
            "login_type": "BATCH",
            "access_level": "FULL_STUDENT",
            "user": batch_user.to_dict()
        }), 200

    # =========================================================
    # EMAIL LOGIN
    # =========================================================

    email_user = User.query.filter_by(
        email=identifier.lower()
    ).first()

    if email_user:

        if not check_password_hash(
            email_user.password,
            password
        ):
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        if email_user.status != "ACTIVE":
            return jsonify({
                "message": "Your account is inactive"
            }), 403

        # Student ambaye tayari amepewa Batch Number
        # hawezi tena kutumia Email kuingia.
        if email_user.role == "STUDENT":

            if email_user.batch_number:
                return jsonify({
                    "message": (
                        "Your application has been approved. "
                        "Please logout and login using your "
                        "Batch Number and your existing password."
                    ),
                    "requires_batch_login": True
                }), 403

            return jsonify({
                "message": "Login successful",
                "login_type": "EMAIL",
                "access_level": "APPLICATION",
                "user": email_user.to_dict()
            }), 200

        return jsonify({
            "message": "Login successful",
            "login_type": "ROLE",
            "access_level": email_user.role,
            "user": email_user.to_dict()
        }), 200

    # =========================================================
    # INSTITUTIONAL ID LOGIN
    # =========================================================

    institutional_user = User.query.filter_by(
        institutional_id=identifier
    ).first()

    if institutional_user:

        if not check_password_hash(
            institutional_user.password,
            password
        ):
            return jsonify({
                "message": "Invalid login credentials"
            }), 401

        if institutional_user.status != "ACTIVE":
            return jsonify({
                "message": "Your account is inactive"
            }), 403

        if institutional_user.role == "STUDENT":

            if institutional_user.batch_number:
                return jsonify({
                    "message": (
                        "Please login using your Batch Number."
                    ),
                    "requires_batch_login": True
                }), 403

            return jsonify({
                "message": "Login successful",
                "login_type": "EMAIL",
                "access_level": "APPLICATION",
                "user": institutional_user.to_dict()
            }), 200

        return jsonify({
            "message": "Login successful",
            "login_type": "ROLE",
            "access_level": institutional_user.role,
            "user": institutional_user.to_dict()
        }), 200

    return jsonify({
        "message": "Invalid login credentials"
    }), 401


@auth_bp.route("/change-password", methods=["PUT"])
def change_password():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if (
        not user_id
        or not current_password
        or not new_password
    ):
        return jsonify({
            "message": (
                "user_id, current_password and "
                "new_password are required"
            )
        }), 400

    if not validate_password(new_password):
        return jsonify({
            "message": (
                "New password must contain at least "
                "8 characters, one capital letter, "
                "one number and one symbol"
            )
        }), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if not check_password_hash(
        user.password,
        current_password
    ):
        return jsonify({
            "message": "Current password is incorrect"
        }), 401

    user.password = generate_password_hash(
        new_password
    )

    db.session.commit()

    return jsonify({
        "message": "Password updated successfully"
    }), 200



# =========================================================
# FORGOT PASSWORD - EMAIL VERIFICATION CODE
# =========================================================

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json() or {}

    identifier = (
        data.get("identifier")
        or data.get("email")
        or ""
    ).strip().lower()

    if not identifier:
        return jsonify({
            "message": "Email is required"
        }), 400

    user = User.query.filter(
        db.func.lower(User.email) == identifier
    ).first()

    if not user:
        return jsonify({
            "message": (
                "If the email exists, a verification "
                "code has been sent."
            )
        }), 200

    # Invalidate previous unused codes
    PasswordResetToken.query.filter_by(
        user_id=user.id,
        used=False
    ).update({
        "used": True
    })

    # Generate 6-digit verification code
    code = f"{secrets.randbelow(1000000):06d}"

    token_hash = hashlib.sha256(
        code.encode()
    ).hexdigest()

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        used=False
    )

    db.session.add(reset_token)
    db.session.commit()

    try:
        send_email(
            user.email,
            "SFPMS Password Reset Verification Code",
            f"""Dear {user.name},

We received a request to reset your SFPMS password.

Your verification code is:

{code}

This code will expire in 10 minutes.

Enter this code in the SFPMS Password Reset page to create
a new password.

If you did not request a password reset, please ignore this email.

Kind regards,
SFPMS Administration
Student Field Placement Management System
"""
        )

    except Exception as email_error:

        db.session.delete(reset_token)
        db.session.commit()

        print(
            f"Password reset email failed for "
            f"{user.email}: {email_error}"
        )

        return jsonify({
            "message": "Failed to send verification code"
        }), 500

    return jsonify({
        "message": (
            "A 6-digit verification code has been "
            "sent to your email."
        )
    }), 200


# =========================================================
# RESET PASSWORD - VERIFY CODE
# =========================================================

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json() or {}

    identifier = (
        data.get("identifier")
        or data.get("email")
        or ""
    ).strip().lower()

    code = (
        data.get("code")
        or ""
    ).strip()

    new_password = data.get("password") or ""

    if not identifier or not code or not new_password:
        return jsonify({
            "message": (
                "Email, verification code and "
                "password are required"
            )
        }), 400

    if not code.isdigit() or len(code) != 6:
        return jsonify({
            "message": "Verification code must be 6 digits"
        }), 400

    if not validate_password(new_password):
        return jsonify({
            "message": (
                "Password must contain at least "
                "8 characters, one capital letter, "
                "one number and one symbol"
            )
        }), 400

    user = User.query.filter(
        db.func.lower(User.email) == identifier
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid verification code"
        }), 400

    token_hash = hashlib.sha256(
        code.encode()
    ).hexdigest()

    reset_token = PasswordResetToken.query.filter_by(
        user_id=user.id,
        token_hash=token_hash,
        used=False
    ).first()

    if not reset_token:
        return jsonify({
            "message": "Invalid verification code"
        }), 400

    if reset_token.expires_at < datetime.utcnow():

        reset_token.used = True
        db.session.commit()

        return jsonify({
            "message": (
                "Verification code has expired. "
                "Please request a new code."
            )
        }), 400

    user.password = generate_password_hash(
        new_password
    )

    reset_token.used = True

    db.session.commit()

    return jsonify({
        "message": "Password reset successfully"
    }), 200
