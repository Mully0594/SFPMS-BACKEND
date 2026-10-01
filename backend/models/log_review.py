from database import db


class LogReview(db.Model):
    __tablename__ = "log_reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    log_id = db.Column(
        db.Integer,
        db.ForeignKey("daily_logs.id"),
        nullable=False
    )

    supervisor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    comment = db.Column(
        db.Text
    )

    decision = db.Column(
        db.String(30)
    )

    reviewed_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "log_id": self.log_id,
            "supervisor_id": self.supervisor_id,
            "comment": self.comment,
            "decision": self.decision,
            "reviewed_at": str(self.reviewed_at) if self.reviewed_at else None,
        }
