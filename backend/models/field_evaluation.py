from database import db


class FieldEvaluation(db.Model):
    """
    A field supervisor's evaluation of a student's performance at
    the host organization, one per student per placement.
    """

    __tablename__ = "field_evaluations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    supervisor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    placement_id = db.Column(
        db.Integer,
        db.ForeignKey("placements.id")
    )

    attendance_score = db.Column(db.Integer)
    discipline_score = db.Column(db.Integer)
    skills_score = db.Column(db.Integer)
    teamwork_score = db.Column(db.Integer)
    overall_score = db.Column(db.Integer)

    comments = db.Column(db.Text)

    status = db.Column(
        db.String(30),
        default="PENDING"
    )

    submitted_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "supervisor_id": self.supervisor_id,
            "placement_id": self.placement_id,
            "attendance_score": self.attendance_score,
            "discipline_score": self.discipline_score,
            "skills_score": self.skills_score,
            "teamwork_score": self.teamwork_score,
            "overall_score": self.overall_score,
            "comments": self.comments,
            "status": self.status,
            "submitted_at": str(self.submitted_at) if self.submitted_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
