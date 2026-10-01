"""
Idempotent migration helper for SFPMS.

db.create_all() only creates tables that don't exist yet - it will
never add a new column to a table that's already there. Since this
project ships with a populated sfpms_db.sql dump (real dev data),
this script inspects the live database and ALTERs existing tables
to add any columns the updated models introduced, then calls
db.create_all() to create the brand-new tables
(applications, field_evaluations, academic_remarks,
system_settings).

Safe to re-run any number of times - it only adds what's missing.

Usage:
    python migrate.py
"""

from sqlalchemy import inspect, text

from app import app, db


# table -> [(column_name, DDL type), ...]
NEW_COLUMNS = {
    "users": [
        ("phone", "VARCHAR(30)"),
    ],
    "organizations": [
        ("organization_code", "VARCHAR(30)"),
        ("type", "VARCHAR(50)"),
        ("region", "VARCHAR(100)"),
        ("district", "VARCHAR(100)"),
        ("email", "VARCHAR(100)"),
        ("phone", "VARCHAR(30)"),
        ("departments", "VARCHAR(255)"),
        ("positions", "INT DEFAULT 0"),
        ("status", "VARCHAR(30) DEFAULT 'ACTIVE'"),
    ],
    "placements": [
        ("application_id", "INT"),
        ("department", "VARCHAR(150)"),
    ],
    "reports": [
        ("title", "VARCHAR(150)"),
        ("description", "TEXT"),
        ("status", "VARCHAR(30) DEFAULT 'PENDING'"),
        ("feedback", "TEXT"),
        ("reviewed_by", "INT"),
        ("reviewed_at", "DATETIME"),
    ],
    "supervisor_assignment": [
        ("role", "VARCHAR(30)"),
        ("assigned_at", "TIMESTAMP NULL"),
    ],
    "notifications": [
        ("type", "VARCHAR(50)"),
    ],
}


def add_missing_columns():
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    with db.engine.connect() as connection:
        for table, columns in NEW_COLUMNS.items():
            if table not in existing_tables:
                # Table doesn't exist yet - db.create_all() will
                # create it fully, nothing to patch here.
                continue

            existing_columns = {
                col["name"] for col in inspector.get_columns(table)
            }

            for column_name, ddl_type in columns:
                if column_name in existing_columns:
                    continue

                print(f"Adding column {table}.{column_name} ...")

                connection.execute(text(
                    f"ALTER TABLE `{table}` ADD COLUMN `{column_name}` {ddl_type}"
                ))

        connection.commit()


def backfill_organization_codes():
    from models import Organization

    organizations = Organization.query.filter(
        (Organization.organization_code.is_(None)) |
        (Organization.organization_code == "")
    ).all()

    for index, organization in enumerate(organizations, start=1):
        organization.organization_code = f"ORG{organization.id:03d}"

    if organizations:
        db.session.commit()
        print(f"Backfilled organization_code for {len(organizations)} organization(s).")


def main():
    with app.app_context():
        print("Patching existing tables with new columns...")
        add_missing_columns()

        print("Creating any brand-new tables...")
        db.create_all()

        print("Backfilling organization codes...")
        backfill_organization_codes()

        print("Migration complete.")


if __name__ == "__main__":
    main()
