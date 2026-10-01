from database import db


class WeeklySummary(db.Model):
    __tablename__ = "weekly_summaries"

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

    week_start = db.Column(
        db.Date,
        nullable=False
    )

    week_end = db.Column(
        db.Date,
        nullable=False
    )

    summary = db.Column(
        db.Text,
        nullable=False,
        default=""
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="PENDING"
    )

    last_submitted_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "placement_id": self.placement_id,
            "week_start": (
                str(self.week_start)
                if self.week_start
                else None
            ),
            "week_end": (
                str(self.week_end)
                if self.week_end
                else None
            ),
            "summary": self.summary or "",
            "status": self.status,
            "last_submitted_at": (
                self.last_submitted_at.isoformat()
                if self.last_submitted_at
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            )
        }