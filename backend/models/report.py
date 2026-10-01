from database import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    placement_id = db.Column(
        db.Integer,
        db.ForeignKey("placements.id"),
        nullable=False
    )

    title = db.Column(
        db.String(150)
    )

    description = db.Column(
        db.Text
    )

    report_type = db.Column(
        db.String(50)
    )

    file_path = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(30),
        default="PENDING"
    )

    feedback = db.Column(
        db.Text
    )

    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    reviewed_at = db.Column(
        db.DateTime
    )

    submitted_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "placement_id": self.placement_id,
            "title": self.title,
            "description": self.description,
            "report_type": self.report_type,
            "file_path": self.file_path,
            "status": self.status,
            "feedback": self.feedback,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": str(self.reviewed_at) if self.reviewed_at else None,
            "submitted_at": str(self.submitted_at) if self.submitted_at else None,
        }
