from flask import Blueprint, request, jsonify

from models.location import Location


locations_bp = Blueprint("locations", __name__)


@locations_bp.route("/", methods=["GET"])
def get_locations():
    """
    Examples:
      /api/locations?level=COUNTRY
      /api/locations?level=REGION&parent_id=1
      /api/locations?level=DISTRICT&parent_id=5
      /api/locations?level=WARD&parent_id=20
    """

    level = request.args.get("level", "").strip().upper()
    parent_id = request.args.get("parent_id")

    if not level:
        return jsonify({
            "message": "level is required"
        }), 400

    query = Location.query.filter_by(
        level_name=level,
        is_active=True
    )

    if level == "COUNTRY":
        query = query.filter(
            Location.parent_id.is_(None)
        )
    else:
        if not parent_id:
            return jsonify({
                "message": "parent_id is required for this level"
            }), 400

        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            return jsonify({
                "message": "parent_id must be a valid number"
            }), 400

        query = query.filter_by(parent_id=parent_id)

    locations = query.order_by(Location.name.asc()).all()

    return jsonify([
        location.to_dict()
        for location in locations
    ]), 200