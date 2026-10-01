from database import db


class SystemSetting(db.Model):
    """
    Single-row table holding the admin System Settings form values.
    A row with id=1 is created on first access if none exists.
    """

    __tablename__ = "system_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ---- General ----
    system_name = db.Column(
        db.String(150),
        default="Student Field Placement Management System"
    )
    institution_name = db.Column(db.String(150), default="Zanzibar Government")
    email = db.Column(db.String(100), default="info@sfpms.com")
    phone = db.Column(db.String(30), default="+255 777 000 000")
    address = db.Column(db.String(255), default="Zanzibar, Tanzania")
    academic_year = db.Column(db.String(20), default="2026/2027")
    placement_period = db.Column(db.String(100), default="September - December")

    # ---- Applications ----
    application_open = db.Column(db.Boolean, default=True)
    application_deadline = db.Column(db.Date)
    allow_application_edit = db.Column(db.Boolean, default=True)
    require_admin_approval = db.Column(db.Boolean, default=True)
    require_supervisor_approval = db.Column(db.Boolean, default=True)

    # ---- Placement ----
    placement_start_date = db.Column(db.Date)
    placement_end_date = db.Column(db.Date)
    max_students_organization = db.Column(db.Integer, default=10)
    placement_approval = db.Column(db.Boolean, default=True)

    # ---- Notifications ----
    email_notification = db.Column(db.Boolean, default=True)
    new_application_notification = db.Column(db.Boolean, default=True)
    approval_notification = db.Column(db.Boolean, default=True)
    rejection_notification = db.Column(db.Boolean, default=True)
    placement_notification = db.Column(db.Boolean, default=True)
    logbook_notification = db.Column(db.Boolean, default=True)

    # ---- Security ----
    minimum_password_length = db.Column(db.Integer, default=8)
    session_timeout = db.Column(db.Integer, default=30)
    allow_student_registration = db.Column(db.Boolean, default=True)
    email_verification = db.Column(db.Boolean, default=False)
    account_lockout = db.Column(db.Boolean, default=True)

    # ---- Logbook ----
    require_daily_entry = db.Column(db.Boolean, default=True)
    logbook_approval = db.Column(db.Boolean, default=True)
    allow_edit_submitted_log = db.Column(db.Boolean, default=False)
    working_hours = db.Column(db.Integer, default=8)
    minimum_required_days = db.Column(db.Integer, default=30)

    # ---- Reports ----
    report_institution_name = db.Column(db.String(150), default="Zanzibar Government")
    report_footer = db.Column(
        db.String(255),
        default="Student Field Placement Management System"
    )
    show_logo_on_report = db.Column(db.Boolean, default=True)
    show_signature = db.Column(db.Boolean, default=True)
    date_format = db.Column(db.String(20), default="DD/MM/YYYY")

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "systemName": self.system_name,
            "institutionName": self.institution_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "academicYear": self.academic_year,
            "placementPeriod": self.placement_period,

            "applicationOpen": bool(self.application_open),
            "applicationDeadline": str(self.application_deadline) if self.application_deadline else None,
            "allowApplicationEdit": bool(self.allow_application_edit),
            "requireAdminApproval": bool(self.require_admin_approval),
            "requireSupervisorApproval": bool(self.require_supervisor_approval),

            "placementStartDate": str(self.placement_start_date) if self.placement_start_date else None,
            "placementEndDate": str(self.placement_end_date) if self.placement_end_date else None,
            "maxStudentsOrganization": self.max_students_organization,
            "placementApproval": bool(self.placement_approval),

            "emailNotification": bool(self.email_notification),
            "newApplicationNotification": bool(self.new_application_notification),
            "approvalNotification": bool(self.approval_notification),
            "rejectionNotification": bool(self.rejection_notification),
            "placementNotification": bool(self.placement_notification),
            "logbookNotification": bool(self.logbook_notification),

            "minimumPasswordLength": self.minimum_password_length,
            "sessionTimeout": self.session_timeout,
            "allowStudentRegistration": bool(self.allow_student_registration),
            "emailVerification": bool(self.email_verification),
            "accountLockout": bool(self.account_lockout),

            "requireDailyEntry": bool(self.require_daily_entry),
            "logbookApproval": bool(self.logbook_approval),
            "allowEditSubmittedLog": bool(self.allow_edit_submitted_log),
            "workingHours": self.working_hours,
            "minimumRequiredDays": self.minimum_required_days,

            "reportInstitutionName": self.report_institution_name,
            "reportFooter": self.report_footer,
            "showLogoOnReport": bool(self.show_logo_on_report),
            "showSignature": bool(self.show_signature),
            "dateFormat": self.date_format,
        }

    # Maps camelCase frontend keys -> snake_case column names so the
    # settings route can update the row generically from the JSON body.
    FIELD_MAP = {
        "systemName": "system_name",
        "institutionName": "institution_name",
        "email": "email",
        "phone": "phone",
        "address": "address",
        "academicYear": "academic_year",
        "placementPeriod": "placement_period",
        "applicationOpen": "application_open",
        "applicationDeadline": "application_deadline",
        "allowApplicationEdit": "allow_application_edit",
        "requireAdminApproval": "require_admin_approval",
        "requireSupervisorApproval": "require_supervisor_approval",
        "placementStartDate": "placement_start_date",
        "placementEndDate": "placement_end_date",
        "maxStudentsOrganization": "max_students_organization",
        "placementApproval": "placement_approval",
        "emailNotification": "email_notification",
        "newApplicationNotification": "new_application_notification",
        "approvalNotification": "approval_notification",
        "rejectionNotification": "rejection_notification",
        "placementNotification": "placement_notification",
        "logbookNotification": "logbook_notification",
        "minimumPasswordLength": "minimum_password_length",
        "sessionTimeout": "session_timeout",
        "allowStudentRegistration": "allow_student_registration",
        "emailVerification": "email_verification",
        "accountLockout": "account_lockout",
        "requireDailyEntry": "require_daily_entry",
        "logbookApproval": "logbook_approval",
        "allowEditSubmittedLog": "allow_edit_submitted_log",
        "workingHours": "working_hours",
        "minimumRequiredDays": "minimum_required_days",
        "reportInstitutionName": "report_institution_name",
        "reportFooter": "report_footer",
        "showLogoOnReport": "show_logo_on_report",
        "showSignature": "show_signature",
        "dateFormat": "date_format",
    }

    DATE_FIELDS = {
        "application_deadline",
        "placement_start_date",
        "placement_end_date"
    }
