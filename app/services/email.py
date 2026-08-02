import smtplib
import logging
from email.message import EmailMessage
from core.config import EMAIL, EMAIL_PASSWORD

logger = logging.getLogger(__name__)
    
def send_otp_email(receiver_email: str,otp : str):
    try:

        # Create email
        message = EmailMessage()

        message["From"] = EMAIL
        message["To"] = receiver_email
        message["Subject"] = "Welcome to Expense Tracker"

        message.set_content(
    f"""
Hello,

Thank you for registering with Expense Tracker.
Your verification OTP is:
{otp}

This OTP is valid for 5 minutes.
Do not share this OTP with anyone.

Regards,
Meet Pandit
"""
)
        # Connect to Gmail
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(
                EMAIL,
                EMAIL_PASSWORD,
            )
            smtp.send_message(message)
        logger.info(
            "Welcome email sent successfully to '%s'",
            receiver_email,
        )

    except Exception as e:
        logger.error(
            "Failed to send email to '%s'. Error: %s",
            receiver_email,
            e,
        )

def send_forgot_password_otp_email(receiver_email: str, otp: str):
    """
    Send a password-reset OTP email.
    """
    try:
        message = EmailMessage()
        message["From"] = EMAIL
        message["To"] = receiver_email
        message["Subject"] = "Expense Tracker — Password Reset OTP"
        message.set_content(
    f"""
Hello,

We received a request to reset your Expense Tracker password.
Your password reset OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request a password reset, please ignore this email.
Your password will remain unchanged.

Do not share this OTP with anyone.

Regards,
Meet Pandit
"""
)
        with smtplib.SMTP("smtp.gmail.com", 144) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, EMAIL_PASSWORD)
            smtp.send_message(message)

        logger.info("Password reset OTP sent successfully to '%s'", receiver_email)

    except Exception as e:
        logger.error(
            "Failed to send password reset email to '%s'. Error: %s",
            receiver_email,
            e,
        )
        