from database import db
from models.user import User


class DailyLog(db.Model):
    __tablename__ = "daily_logs"

    id = db.Column(db.Integer, primary_key=True)

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

    log_date = db.Column(
        db.Date,
        nullable=False
    )

    sign_in_time = db.Column(db.Time)

    sign_in_latitude = db.Column(db.Numeric(10, 8))

    sign_in_longitude = db.Column(db.Numeric(11, 8))

    sign_out_time = db.Column(db.Time)

    sign_out_latitude = db.Column(db.Numeric(10, 8))

    sign_out_longitude = db.Column(db.Numeric(11, 8))

    activity = db.Column(
        db.Text,
        nullable=True,
        default=""
    )

    attachment = db.Column(
        db.String(255),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="PENDING"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "placement_id": self.placement_id,
            "log_date": str(self.log_date) if self.log_date else None,
            "sign_in_time": str(self.sign_in_time) if self.sign_in_time else None,
            "sign_in_latitude": float(self.sign_in_latitude) if self.sign_in_latitude is not None else None,
            "sign_in_longitude": float(self.sign_in_longitude) if self.sign_in_longitude is not None else None,
            "sign_out_time": str(self.sign_out_time) if self.sign_out_time else None,
            "sign_out_latitude": float(self.sign_out_latitude) if self.sign_out_latitude is not None else None,
            "sign_out_longitude": float(self.sign_out_longitude) if self.sign_out_longitude is not None else None,
            "activity": self.activity or "",
            "attachment": self.attachment,
            "status": self.status
        }

    def to_dict_with_student(self):
        student = User.query.get(self.student_id)

        data = self.to_dict()

        data["student_name"] = student.name if student else None

        data["student"] = {
            "id": student.id,
            "name": student.name,
            "institutional_id": student.institutional_id,
            "email": student.email,
            "programme": student.programme
        } if student else None

        data["attachment_url"] = (
            f"/api/daily-logs/uploads/{self.attachment}"
            if self.attachment
            else None
        )

        return data