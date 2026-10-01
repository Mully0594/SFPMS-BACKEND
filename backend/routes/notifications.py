from flask import Blueprint, request, jsonify

from database import db
from models import Notification, User


notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["POST"])
def create_notification():

    data = request.get_json()

    user_id = data.get("user_id")
    message = data.get("message")
    notif_type = data.get("type")

    if not user_id or not message:
        return jsonify({
            "message": "user_id and message are required"
        }), 400

    if not User.query.get(user_id):
        return jsonify({"message": "User not found"}), 404

    notification = Notification(
        user_id=user_id,
        message=message,
        type=notif_type
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Notification created successfully",
        "notification": notification.to_dict()
    }), 201


@notifications_bp.route("/", methods=["GET"])
def get_notifications():

    query = Notification.query

    user_id = request.args.get("user_id")
    unread_only = request.args.get("unread_only")

    if user_id:
        query = query.filter(Notification.user_id == user_id)

    if unread_only in ("true", "1", "yes"):
        query = query.filter(Notification.is_read.is_(False))

    notifications = query.order_by(Notification.created_at.desc()).all()

    return jsonify([notification.to_dict() for notification in notifications]), 200


@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
def mark_read(notification_id):

    notification = Notification.query.get(notification_id)

    if not notification:
        return jsonify({"message": "Notification not found"}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({
        "message": "Notification marked as read",
        "notification": notification.to_dict()
    }), 200


@notifications_bp.route("/mark-all-read", methods=["PUT"])
def mark_all_read():

    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    Notification.query.filter_by(user_id=user_id, is_read=False).update(
        {"is_read": True}
    )
    db.session.commit()

    return jsonify({"message": "All notifications marked as read"}), 200


@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):

    notification = Notification.query.get(notification_id)

    if not notification:
        return jsonify({"message": "Notification not found"}), 404

    db.session.delete(notification)
    db.session.commit()

    return jsonify({"message": "Notification deleted successfully"}), 200
