from flask_mail import Message
from flask import current_app


def send_approval_email(
    student_email,
    student_name,
    batch_number
):
    msg = Message(
        subject="SFPMS Application Approved",
        recipients=[student_email],
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )

    msg.body = f"""Dear {student_name},

We are pleased to inform you that your Student Field Placement application has been APPROVED.

Your SFPMS Batch Number is:

{batch_number}

Please logout from your current session and login again using:

Batch Number: {batch_number}
Password: Your existing password

After logging in with your Batch Number, you will have access to:
- Placement
- Daily Logs
- Reports

Please keep your Batch Number safe.

Kind regards,
SFPMS Administration
Student Field Placement Management System
"""

    from app import mail
    mail.send(msg)
