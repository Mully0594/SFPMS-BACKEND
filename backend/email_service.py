import os
import resend


def send_email(to, subject, text):
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv(
        "RESEND_FROM_EMAIL",
        "onboarding@resend.dev"
    )

    if not api_key:
        raise Exception("RESEND_API_KEY is not configured")

    resend.api_key = api_key

    params = {
        "from": from_email,
        "to": [to],
        "subject": subject,
        "text": text,
    }

    return resend.Emails.send(params)


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

    return send_email(
        student_email,
        subject,
        body
    )
