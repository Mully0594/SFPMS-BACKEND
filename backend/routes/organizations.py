id="m9w0yc"
import random
import string

from flask import Blueprint, request, jsonify

from database import db
from models import Organization, Placement


organizations_bp = Blueprint("organizations", __name__)


VALID_STATUSES = {
    "PENDING",
    "ACTIVE",
    "INACTIVE"
}


def _generate_org_code():
    while True:
        code = "ORG" + "".join(
            random.choices(string.digits, k=3)
        )

        if not Organization.query.filter_by(
            organization_code=code
        ).first():
            return code


def _normalize_status(status):
    status = str(status or "ACTIVE").strip().upper()

    if status not in VALID_STATUSES:
        return None

    return status


def _apply_fields(organization, data):
    fields = [
        "name",
        "type",
        "address",
        "region",
        "district",
        "email",
        "phone",
        "contact_person",
        "contact_phone",
        "departments"
    ]

    for field in fields:
        if field in data:
            value = data[field]

            if isinstance(value, str):
                value = value.strip()

            setattr(organization, field, value)

    if "positions" in data:
        try:
            positions = int(data["positions"] or 0)

            if positions < 0:
                return False, "positions cannot be negative"

            organization.positions = positions

        except (TypeError, ValueError):
            return False, "positions must be a valid number"

    if "status" in data:
        status = _normalize_status(data["status"])

        if not status:
            return False, "Invalid organization status"

        organization.status = status

    return True, None


@organizations_bp.route("/", methods=["POST"])
def create_organization():
    data = request.get_json() or {}

    name = str(data.get("name") or "").strip()

    if not name:
        return jsonify({
            "message": "Organization name is required"
        }), 400

    existing = Organization.query.filter(
        Organization.name.ilike(name)
    ).first()

    if existing:
        return jsonify({
            "message": "Organization already exists"
        }), 409

    status = _normalize_status(
        data.get("status", "ACTIVE")
    )

    if not status:
        return jsonify({
            "message": "Invalid organization status"
        }), 400

    new_organization = Organization(
        organization_code=_generate_org_code(),
        name=name,
        status=status
    )

    success, error = _apply_fields(
        new_organization,
        data
    )

    if not success:
        return jsonify({
            "message": error
        }), 400

    new_organization.name = name

    db.session.add(new_organization)
    db.session.commit()

    return jsonify({
        "message": "Organization created successfully",
        "organization": new_organization.to_dict()
    }), 201


@organizations_bp.route("/register", methods=["POST"])
def register_organization():
    data = request.get_json() or {}

    name = str(
        data.get("organizationName")
        or data.get("name")
        or ""
    ).strip()

    contact_person = str(
        data.get("contactPerson")
        or data.get("contact_person")
        or ""
    ).strip()

    phone = str(
        data.get("phone")
        or ""
    ).strip()

    email = str(
        data.get("email")
        or ""
    ).strip()

    if not name or not contact_person or not phone:
        return jsonify({
            "message": (
                "organizationName, contactPerson "
                "and phone are required"
            )
        }), 400

    existing_organization = Organization.query.filter(
        Organization.name.ilike(name)
    ).first()

    if existing_organization:
        return jsonify({
            "message": "Organization already registered"
        }), 409

    new_organization = Organization(
        organization_code=_generate_org_code(),
        name=name,
        contact_person=contact_person,
        contact_phone=phone,
        phone=phone,
        email=email,
        status="PENDING"
    )

    db.session.add(new_organization)
    db.session.commit()

    return jsonify({
        "message": (
            "Organization registration submitted for review"
        ),
        "organization": new_organization.to_dict()
    }), 201


@organizations_bp.route("/", methods=["GET"])
def get_organizations():
    query = Organization.query

    status = request.args.get("status")
    search = request.args.get("search")

    if status:
        status = _normalize_status(status)

        if not status:
            return jsonify({
                "message": "Invalid organization status"
            }), 400

        query = query.filter(
            Organization.status == status
        )

    if search:
        search = search.strip()

        if search:
            like = f"%{search}%"

            query = query.filter(
                (Organization.name.ilike(like)) |
                (Organization.organization_code.ilike(like)) |
                (Organization.region.ilike(like)) |
                (Organization.district.ilike(like))
            )

    organizations = query.order_by(
        Organization.id.desc()
    ).all()

    result = []

    for organization in organizations:
        data = organization.to_dict()

        data["active_students"] = Placement.query.filter_by(
            organization_id=organization.id,
            status="ACTIVE"
        ).count()

        result.append(data)

    return jsonify(result), 200


@organizations_bp.route(
    "/<int:organization_id>",
    methods=["GET"]
)
def get_organization(organization_id):
    organization = Organization.query.get(
        organization_id
    )

    if not organization:
        return jsonify({
            "message": "Organization not found"
        }), 404

    data = organization.to_dict()

    data["active_students"] = Placement.query.filter_by(
        organization_id=organization_id,
        status="ACTIVE"
    ).count()

    data["total_students"] = Placement.query.filter_by(
        organization_id=organization_id
    ).count()

    return jsonify(data), 200


@organizations_bp.route(
    "/<int:organization_id>",
    methods=["PUT"]
)
def update_organization(organization_id):
    organization = Organization.query.get(
        organization_id
    )

    if not organization:
        return jsonify({
            "message": "Organization not found"
        }), 404

    data = request.get_json() or {}

    if "name" in data:
        name = str(
            data.get("name") or ""
        ).strip()

        if not name:
            return jsonify({
                "message": "Organization name is required"
            }), 400

        existing = Organization.query.filter(
            Organization.name.ilike(name),
            Organization.id != organization_id
        ).first()

        if existing:
            return jsonify({
                "message": "Organization already exists"
            }), 409

    success, error = _apply_fields(
        organization,
        data
    )

    if not success:
        return jsonify({
            "message": error
        }), 400

    db.session.commit()

    return jsonify({
        "message": "Organization updated successfully",
        "organization": organization.to_dict()
    }), 200


@organizations_bp.route(
    "/<int:organization_id>/status",
    methods=["PATCH"]
)
def update_organization_status(organization_id):
    organization = Organization.query.get(
        organization_id
    )

    if not organization:
        return jsonify({
            "message": "Organization not found"
        }), 404

    data = request.get_json() or {}

    status = _normalize_status(
        data.get("status")
    )

    if not status:
        return jsonify({
            "message": "Invalid organization status"
        }), 400

    organization.status = status

    if status == "INACTIVE":
        active_placements = Placement.query.filter_by(
            organization_id=organization.id,
            status="ACTIVE"
        ).all()

        for placement in active_placements:
            placement.status = "INACTIVE"

    db.session.commit()

    return jsonify({
        "message": "Organization status updated successfully",
        "organization": organization.to_dict()
    }), 200


@organizations_bp.route(
    "/<int:organization_id>",
    methods=["DELETE"]
)
def delete_organization(organization_id):
    organization = Organization.query.get(
        organization_id
    )

    if not organization:
        return jsonify({
            "message": "Organization not found"
        }), 404

    active_placements = Placement.query.filter_by(
        organization_id=organization.id,
        status="ACTIVE"
    ).count()

    if active_placements > 0:
        organization.status = "INACTIVE"

        placements = Placement.query.filter_by(
            organization_id=organization.id,
            status="ACTIVE"
        ).all()

        for placement in placements:
            placement.status = "INACTIVE"

        db.session.commit()

        return jsonify({
            "message": (
                "Organization has active placements, "
                "so it was deactivated instead of deleted"
            ),
            "organization": organization.to_dict()
        }), 200

    organization.status = "INACTIVE"

    db.session.commit()

    return jsonify({
        "message": "Organization deactivated successfully",
        "organization": organization.to_dict()
    }), 200