from flask import current_app
from flask_mail import Message


def send_email(to, subject, text):
    msg = Message(
        subject=subject,
        recipients=[to],
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )

    msg.body = text

    current_app.extensions["mail"].send(msg)

    return True


def send_approval_email(student_email, student_name, batch_number):
    subject = "SFPMS Application Approved"

    body = f"""Dear {student_name},

Congratulations!

Your SFPMS Student Field Placement application has been APPROVED.

Your Batch Number is:

{batch_number}

You can now log in to the SFPMS system using your Batch Number and password.

Kind regards,
SFPMS Administration
Student Field Placement Management System
"""

    return send_email(student_email, subject, body)
