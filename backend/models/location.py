
from database import db


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    level_name = db.Column(db.String(30), nullable=False)
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("locations.id"),
        nullable=True
    )
    country_code = db.Column(db.String(2))
    is_active = db.Column(db.Boolean, default=True)

    children = db.relationship(
        "Location",
        backref=db.backref("parent", remote_side=[id]),
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "level_name": self.level_name,
            "parent_id": self.parent_id,
            "country_code": self.country_code
        }