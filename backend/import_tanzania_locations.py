"""
Import Tanzania administrative divisions from hierarchy.json into SFPMS locations.

Run from the backend directory (the directory containing app.py):
    python import_tanzania_locations.py

Expected project imports:
    from app import app
    from database import db
    from models.location import Location

The importer uses name + level + parent_id to avoid duplicate rows.
"""
import json
from pathlib import Path

from app import app
from database import db
from models.location import Location

JSON_PATH = Path(__file__).resolve().parent / "hierarchy.json"


def location_exists(name, level_name, parent_id):
    query = Location.query.filter_by(
        name=name,
        level_name=level_name,
        parent_id=parent_id,
    )
    return query.first()


def add_location(name, level_name, parent_id=None, country_code="TZ"):
    existing = location_exists(name, level_name, parent_id)
    if existing:
        return existing, False

    row = Location(
        name=name,
        level_name=level_name,
        parent_id=parent_id,
        country_code=country_code,
        is_active=True,
    )
    db.session.add(row)
    db.session.flush()  # obtain generated integer id
    return row, True


def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {JSON_PATH.name}. Put hierarchy.json beside this script."
        )

    with JSON_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    regions = payload.get("data", [])
    if not isinstance(regions, list):
        raise ValueError("Unexpected JSON structure: 'data' must be a list.")

    inserted = {"COUNTRY": 0, "REGION": 0, "DISTRICT": 0, "WARD": 0}
    with app.app_context():
        try:
            country, created = add_location(
                "Tanzania", "COUNTRY", None, "TZ"
            )
            inserted["COUNTRY"] += int(created)

            for region_data in regions:
                region_name = region_data.get("name", {}).get("en") or \
                              region_data.get("name", {}).get("local")
                if not region_name:
                    continue

                region, created = add_location(
                    region_name, "REGION", country.id, "TZ"
                )
                inserted["REGION"] += int(created)

                for district_data in region_data.get("district", []):
                    district_name = district_data.get("name", {}).get("en") or \
                                    district_data.get("name", {}).get("local")
                    if not district_name:
                        continue

                    district, created = add_location(
                        district_name, "DISTRICT", region.id, "TZ"
                    )
                    inserted["DISTRICT"] += int(created)

                    for ward_data in district_data.get("ward", []):
                        ward_name = ward_data.get("name", {}).get("en") or \
                                    ward_data.get("name", {}).get("local")
                        if not ward_name:
                            continue

                        _, created = add_location(
                            ward_name, "WARD", district.id, "TZ"
                        )
                        inserted["WARD"] += int(created)

            db.session.commit()
            print("Tanzania location import completed.")
            print("New records inserted:")
            for level, count in inserted.items():
                print(f"  {level}: {count}")
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()
