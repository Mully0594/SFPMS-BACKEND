from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    institutional_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(30)
    )

    programme = db.Column(
        db.String(100)
    )

    batch_number = db.Column(
        db.String(50),
        nullable=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.Enum(
            "STUDENT",
            "FIELD_SUPERVISOR",
            "ACADEMIC_SUPERVISOR",
            "COORDINATOR",
            "ADMIN"
        ),
        nullable=False
    )

    status = db.Column(
        db.Enum("ACTIVE", "INACTIVE"),
        default="ACTIVE"
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
            "institutional_id": self.institutional_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "programme": self.programme,
            "batch_number": self.batch_number,
            "role": self.role,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }