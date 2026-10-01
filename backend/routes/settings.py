from datetime import datetime

from flask import Blueprint, request, jsonify

from database import db
from models import SystemSetting


settings_bp = Blueprint("settings", __name__)


def _get_settings_row():
    settings = SystemSetting.query.get(1)

    if not settings:
        settings = SystemSetting(id=1)
        db.session.add(settings)
        db.session.commit()

    return settings


@settings_bp.route("/", methods=["GET"])
def get_settings():

    settings = _get_settings_row()

    return jsonify(settings.to_dict()), 200


@settings_bp.route("/", methods=["PUT"])
def update_settings():

    settings = _get_settings_row()

    data = request.get_json() or {}

    for key, value in data.items():
        column = SystemSetting.FIELD_MAP.get(key)

        if not column:
            continue

        if column in SystemSetting.DATE_FIELDS and value:
            try:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "message": f"Invalid date for {key}. Use YYYY-MM-DD"
                }), 400

        setattr(settings, column, value)

    db.session.commit()

    return jsonify({
        "message": "Settings updated successfully",
        "settings": settings.to_dict()
    }), 200
