from database import db


class Application(db.Model):
    """
    A student's field-placement application, matching the multi-step
    form in the frontend's Student > Application page. Once approved,
    an admin/coordinator turns it into an active Placement.
    """

    __tablename__ = "applications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    application_code = db.Column(
        db.String(30),
        unique=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # ---- Personal information ----
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(100))
    national_id = db.Column(db.String(50))

    # ---- Contact information ----
    phone = db.Column(db.String(30))
    email = db.Column(db.String(100))
    alternative_phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    region = db.Column(db.String(100))
    district = db.Column(db.String(100))
    ward = db.Column(db.String(100))

    # ---- Academic information ----
    student_number = db.Column(db.String(50))
    programme = db.Column(db.String(150))
    department = db.Column(db.String(150))
    year_of_study = db.Column(db.String(20))
    academic_year = db.Column(db.String(20))
    institution = db.Column(db.String(150))

    # ---- Field placement preferences ----
    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.id")
    )
    preferred_organization = db.Column(db.String(150))
    organization_type = db.Column(db.String(50))
    preferred_location = db.Column(db.String(150))
    placement_start_date = db.Column(db.Date)
    placement_end_date = db.Column(db.Date)
    placement_duration = db.Column(db.String(50))
    preferred_department = db.Column(db.String(150))
    skills = db.Column(db.Text)
    placement_reason = db.Column(db.Text)

    # ---- Documents ----
    application_letter_path = db.Column(db.String(255))
    cv_path = db.Column(db.String(255))
    student_id_copy_path = db.Column(db.String(255))

    # ---- Workflow ----
    status = db.Column(
        db.String(30),
        default="PENDING"
    )

    rejection_reason = db.Column(db.Text)

    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    reviewed_at = db.Column(db.DateTime)

    submitted_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def student_name(self):
        parts = [
            self.first_name,
            self.middle_name,
            self.last_name
        ]

        return " ".join([p for p in parts if p])

    def to_dict(self):
        return {
            "id": self.id,
            "application_code": self.application_code,
            "student_id": self.student_id,
            "student_name": self.student_name(),
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "date_of_birth": str(self.date_of_birth) if self.date_of_birth else None,
            "nationality": self.nationality,
            "national_id": self.national_id,
            "phone": self.phone,
            "email": self.email,
            "alternative_phone": self.alternative_phone,
            "address": self.address,
            "region": self.region,
            "district": self.district,
            "ward": self.ward,
            "student_number": self.student_number,
            "programme": self.programme,
            "department": self.department,
            "year_of_study": self.year_of_study,
            "academic_year": self.academic_year,
            "institution": self.institution,
            "organization_id": self.organization_id,
            "preferred_organization": self.preferred_organization,
            "organization_type": self.organization_type,
            "preferred_location": self.preferred_location,
            "placement_start_date": str(self.placement_start_date) if self.placement_start_date else None,
            "placement_end_date": str(self.placement_end_date) if self.placement_end_date else None,
            "placement_duration": self.placement_duration,
            "preferred_department": self.preferred_department,
            "skills": self.skills,
            "placement_reason": self.placement_reason,
            "application_letter_path": self.application_letter_path,
            "cv_path": self.cv_path,
            "student_id_copy_path": self.student_id_copy_path,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": str(self.reviewed_at) if self.reviewed_at else None,
            "submitted_at": str(self.submitted_at) if self.submitted_at else None,
        }
