from database import db


class supervisor_assignment(db.Model):
    __tablename__ = "supervisor_assignment"

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

    role = db.Column(
        db.String(30)
    )

    assigned_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "supervisor_id": self.supervisor_id,
            "role": self.role,
            "assigned_at": str(self.assigned_at) if self.assigned_at else None,
        }
