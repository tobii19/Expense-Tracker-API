import logging
import resend

from core.config import RESEND_API_KEY

logger = logging.getLogger(__name__)

resend.api_key = RESEND_API_KEY

FROM_EMAIL = "onboarding@resend.dev"   # Replace with your verified sender later


def send_otp_email(receiver_email: str, otp: str):
    try:

        resend.Emails.send(
            {
                "from": FROM_EMAIL,
                "to": receiver_email,
                "subject": "Expense Tracker - Email Verification OTP",
                "text": f"""
Hello,

Thank you for registering with Expense Tracker.

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
Meet Pandit
""",
            }
        )

        logger.info("OTP email sent successfully to %s", receiver_email)

    except Exception as e:
        logger.error(
            "Failed to send OTP email to '%s'. Error: %s",
            receiver_email,
            e,
        )


def send_forgot_password_otp_email(receiver_email: str, otp: str):
    try:

        resend.Emails.send(
            {
                "from": FROM_EMAIL,
                "to": receiver_email,
                "subject": "Expense Tracker - Password Reset OTP",
                "text": f"""
Hello,

You requested to reset your password.

Your OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Regards,
Meet Pandit
""",
            }
        )

        logger.info(
            "Forgot password OTP sent successfully to %s",
            receiver_email,
        )

    except Exception as e:
        logger.error(
            "Failed to send password reset OTP to '%s'. Error: %s",
            receiver_email,
            e,
        )