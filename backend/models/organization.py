from database import db


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    organization_code = db.Column(
        db.String(30),
        unique=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    type = db.Column(
        db.String(50)
    )

    address = db.Column(
        db.String(255)
    )

    region = db.Column(
        db.String(100)
    )

    district = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(30)
    )

    contact_person = db.Column(
        db.String(100)
    )

    contact_phone = db.Column(
        db.String(30)
    )

    departments = db.Column(
        db.String(255)
    )

    positions = db.Column(
        db.Integer,
        default=0
    )

    status = db.Column(
        db.String(30),
        default="ACTIVE"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "organization_code": self.organization_code,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "region": self.region,
            "district": self.district,
            "email": self.email,
            "phone": self.phone,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "departments": self.departments,
            "positions": self.positions,
            "status": self.status,
        }
