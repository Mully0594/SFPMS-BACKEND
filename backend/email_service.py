import os
import json
import urllib.request
import urllib.error
from flask import current_app


def send_email(to, subject, text):
    api_key = os.getenv("BREVO_API_KEY")

    if not api_key:
        raise Exception("BREVO_API_KEY is not configured")

    sender = current_app.config.get(
        "MAIL_DEFAULT_SENDER",
        "spfmsegaz@gmail.com"
    )

    payload = {
        "sender": {
            "name": "eGAZ student field",
            "email": sender
        },
        "to": [
            {
                "email": to
            }
        ],
        "subject": subject,
        "textContent": text
    }

    request = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        raise Exception(f"Brevo API error: {body}")


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
