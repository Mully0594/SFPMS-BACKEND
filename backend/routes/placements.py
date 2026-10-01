from flask import Blueprint, request, jsonify
from datetime import datetime

from database import db
from models import Placement, User, Organization


placements_bp = Blueprint("placements", __name__)


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@placements_bp.route("/", methods=["POST"])
def create_placement():

    data = request.get_json()

    student_id = data.get("student_id")
    organization_id = data.get("organization_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    department = data.get("department")

    # Check required fields
    if not student_id or not organization_id or not start_date or not end_date:
        return jsonify({
            "message": "student_id, organization_id, start_date and end_date are required"
        }), 400

    # Check student
    student = User.query.get(student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    if student.role != "STUDENT":
        return jsonify({
            "message": "User is not a student"
        }), 400

    # Check organization
    organization = Organization.query.get(organization_id)

    if not organization:
        return jsonify({
            "message": "Organization not found"
        }), 404

    # Convert dates
    try:
        start_date = _parse_date(start_date)
        end_date = _parse_date(end_date)

    except ValueError:
        return jsonify({
            "message": "Invalid date format. Use YYYY-MM-DD"
        }), 400

    # Check date order
    if end_date < start_date:
        return jsonify({
            "message": "End date cannot be before start date"
        }), 400

    # Create placement
    new_placement = Placement(
        student_id=student_id,
        organization_id=organization_id,
        application_id=data.get("application_id"),
        department=department,
        start_date=start_date,
        end_date=end_date,
        status=data.get("status", "ACTIVE")
    )

    db.session.add(new_placement)
    db.session.commit()

    return jsonify({
        "message": "Placement created successfully",
        "placement": new_placement.to_dict()
    }), 201


@placements_bp.route("/", methods=["GET"])
def get_placements():

    query = Placement.query

    student_id = request.args.get("student_id")
    organization_id = request.args.get("organization_id")
    status = request.args.get("status")

    if student_id:
        query = query.filter(Placement.student_id == student_id)

    if organization_id:
        query = query.filter(Placement.organization_id == organization_id)

    if status:
        query = query.filter(Placement.status == status.upper())

    placements = query.order_by(Placement.id.desc()).all()

    return jsonify([placement.to_dict() for placement in placements]), 200


@placements_bp.route("/<int:placement_id>", methods=["GET"])
def get_placement(placement_id):

    placement = Placement.query.get(placement_id)

    if not placement:
        return jsonify({"message": "Placement not found"}), 404

    return jsonify(placement.to_dict()), 200


@placements_bp.route("/<int:placement_id>", methods=["PUT"])
def update_placement(placement_id):

    placement = Placement.query.get(placement_id)

    if not placement:
        return jsonify({"message": "Placement not found"}), 404

    data = request.get_json()

    if "start_date" in data:
        try:
            placement.start_date = _parse_date(data["start_date"])
        except ValueError:
            return jsonify({"message": "Invalid start_date format. Use YYYY-MM-DD"}), 400

    if "end_date" in data:
        try:
            placement.end_date = _parse_date(data["end_date"])
        except ValueError:
            return jsonify({"message": "Invalid end_date format. Use YYYY-MM-DD"}), 400

    if "department" in data:
        placement.department = data["department"]

    if "status" in data:
        placement.status = data["status"].upper()

    db.session.commit()

    return jsonify({
        "message": "Placement updated successfully",
        "placement": placement.to_dict()
    }), 200


@placements_bp.route("/<int:placement_id>", methods=["DELETE"])
def delete_placement(placement_id):

    placement = Placement.query.get(placement_id)

    if not placement:
        return jsonify({"message": "Placement not found"}), 404

    db.session.delete(placement)
    db.session.commit()

    return jsonify({"message": "Placement deleted successfully"}), 200
