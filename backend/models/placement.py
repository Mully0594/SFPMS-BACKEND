from database import db


class Placement(db.Model):
    __tablename__ = "placements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.id"),
        nullable=False
    )

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id")
    )

    department = db.Column(
        db.String(150)
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="ACTIVE"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "organization_id": self.organization_id,
            "application_id": self.application_id,
            "department": self.department,
            "start_date": str(self.start_date) if self.start_date else None,
            "end_date": str(self.end_date) if self.end_date else None,
            "status": self.status,
        }
