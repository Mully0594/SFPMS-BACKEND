import os

from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail

from config import Config
from database import db

from models import (
    User,
    Organization,
    Placement,
    DailyLog,
    supervisor_assignment,
    LogReview,
    Notification,
    Report,
    Application,
    FieldEvaluation,
    AcademicRemark,
    SystemSetting,
    PasswordResetToken,
)

from routes.auth import auth_bp
from routes.users import users_bp
from routes.daily_logs import daily_logs_bp
from routes.log_reviews import log_reviews_bp
from routes.placements import placements_bp
from routes.organizations import organizations_bp
from routes.supervisor_assignment import supervisor_assignment_bp
from routes.notifications import notifications_bp
from routes.applications import applications_bp
from routes.reports import reports_bp
from routes.evaluations import evaluations_bp
from routes.academic_remarks import academic_remarks_bp
from routes.settings import settings_bp
from routes.dashboard import dashboard_bp
from routes.locations import locations_bp


# =========================================================
# CREATE FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# LOAD CONFIGURATION
# =========================================================

app.config.from_object(Config)

# =========================================================
# EMAIL
# =========================================================

mail = Mail(app)


# =========================================================
# CORS CONFIGURATION
# =========================================================

CORS(
    app,
    resources={r"/api/*": {"origins": Config.FRONTEND_ORIGINS}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)


# =========================================================
# FORCE CORS HEADERS
# =========================================================

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin in Config.FRONTEND_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Vary"] = "Origin"

    return response


# =========================================================
# DATABASE

# =========================================================

db.init_app(app)


# =========================================================
# API ROUTES
# =========================================================

app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

app.register_blueprint(
    users_bp,
    url_prefix="/api/users"
)

app.register_blueprint(
    daily_logs_bp,
    url_prefix="/api/daily-logs"
)

app.register_blueprint(
    log_reviews_bp,
    url_prefix="/api/log-reviews"
)

app.register_blueprint(
    placements_bp,
    url_prefix="/api/placements"
)

app.register_blueprint(
    organizations_bp,
    url_prefix="/api/organizations"
)

app.register_blueprint(
    supervisor_assignment_bp,
    url_prefix="/api/supervisor-assignment"
)

app.register_blueprint(
    notifications_bp,
    url_prefix="/api/notifications"
)

app.register_blueprint(
    applications_bp,
    url_prefix="/api/applications"
)

app.register_blueprint(
    reports_bp,
    url_prefix="/api/reports"
)

app.register_blueprint(
    evaluations_bp,
    url_prefix="/api/evaluations"
)

app.register_blueprint(
    academic_remarks_bp,
    url_prefix="/api/academic-remarks"
)

app.register_blueprint(
    settings_bp,
    url_prefix="/api/settings"
)

app.register_blueprint(
    dashboard_bp,
    url_prefix="/api/dashboard"
)

app.register_blueprint(
    locations_bp,
    url_prefix="/api/locations"
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return {
        "message": "SFPMS Backend is running successfully",
        "server": "0.0.0.0",
        "port": 5000
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():
    return {
        "status": "ok",
        "service": "sfpms-backend",
        "server": "0.0.0.0",
        "port": 5000
    }



# =========================================================
# UPLOADED FILES - SYSTEM WIDE
# =========================================================

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/api/uploads/<path:filename>")
def api_uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.errorhandler(404)
def not_found(error):
    return {
        "message": "API endpoint not found",
        "error": "Not Found"
    }, 404


@app.errorhandler(405)
def method_not_allowed(error):
    return {
        "message": "HTTP method not allowed",
        "error": "Method Not Allowed"
    }, 405


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()

    return {
        "message": "Internal server error",
        "error": "Internal Server Error"
    }, 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SFPMS BACKEND")
    print("=" * 60)
    print("Local:   http://127.0.0.1:5000")
    print("Network: http://172.16.18.87:5000")
    print("API:     http://172.16.18.87:5000/api")
    print("Health:  http://172.16.18.87:5000/api/health")
    print("=" * 60)

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )