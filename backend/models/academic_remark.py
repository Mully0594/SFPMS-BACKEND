from database import db


class AcademicRemark(db.Model):
    """
    An academic supervisor's remarks/scoring of a student's field
    placement progress, matching the AcademicRemarks frontend page.
    """

    __tablename__ = "academic_remarks"

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

    practical_skills = db.Column(db.Integer)
    professional_conduct = db.Column(db.Integer)
    academic_progress = db.Column(db.Integer)
    attendance = db.Column(db.Integer)

    strengths = db.Column(db.Text)
    improvement = db.Column(db.Text)
    remarks = db.Column(db.Text)
    recommendation = db.Column(db.Text)

    rating = db.Column(db.String(30))

    submitted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
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
            "practical_skills": self.practical_skills,
            "professional_conduct": self.professional_conduct,
            "academic_progress": self.academic_progress,
            "attendance": self.attendance,
            "strengths": self.strengths,
            "improvement": self.improvement,
            "remarks": self.remarks,
            "recommendation": self.recommendation,
            "rating": self.rating,
            "submitted": bool(self.submitted),
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
