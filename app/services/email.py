import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import resend

from core.config import RESEND_API_KEY, EMAIL, EMAIL_PASSWORD

logger = logging.getLogger(__name__)

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

FROM_EMAIL = "onboarding@resend.dev"   # Replace with your verified sender later


def send_email_via_smtp(receiver_email: str, subject: str, text_content: str) -> bool:
    """
    Sends an email using standard SMTP.
    Utilizes EMAIL and EMAIL_PASSWORD environment variables.
    """
    if not EMAIL or not EMAIL_PASSWORD:
        logger.warning("SMTP credentials (EMAIL/EMAIL_PASSWORD) not configured. Skipping SMTP.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(text_content, "plain"))

        # Determine SMTP server based on email provider (default to Gmail)
        smtp_server = "smtp.gmail.com"
        port = 587

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, receiver_email, msg.as_string())
        server.quit()
        logger.info("Email sent successfully via SMTP to %s", receiver_email)
        return True
    except Exception as e:
        logger.error("Failed to send email via SMTP to '%s'. Error: %s", receiver_email, e)
        return False


def send_otp_email(receiver_email: str, otp: str):
    subject = "Expense Tracker - Email Verification OTP"
    body = f"""Hello,

Thank you for registering with Expense Tracker.

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
Meet Pandit
"""
    # 1. Try sending via SMTP (Gmail App Password)
    if EMAIL and EMAIL_PASSWORD:
        logger.info("Attempting to send OTP email to %s via SMTP...", receiver_email)
        success = send_email_via_smtp(receiver_email, subject, body)
        if success:
            return

    # 2. Fallback to Resend API
    if RESEND_API_KEY:
        logger.info("Attempting to send OTP email to %s via Resend...", receiver_email)
        try:
            resend.Emails.send(
                {
                    "from": FROM_EMAIL,
                    "to": receiver_email,
                    "subject": subject,
                    "text": body,
                }
            )
            logger.info("OTP email sent successfully to %s via Resend", receiver_email)
        except Exception as e:
            logger.error(
                "Failed to send OTP email to '%s' via Resend. Error: %s",
                receiver_email,
                e,
            )
    else:
        logger.error("No email delivery mechanism configured. Could not send email to %s", receiver_email)


def send_forgot_password_otp_email(receiver_email: str, otp: str):
    subject = "Expense Tracker - Password Reset OTP"
    body = f"""Hello,

You requested to reset your password.

Your OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Regards,
Meet Pandit
"""
    # 1. Try sending via SMTP (Gmail App Password)
    if EMAIL and EMAIL_PASSWORD:
        logger.info("Attempting to send forgot password email to %s via SMTP...", receiver_email)
        success = send_email_via_smtp(receiver_email, subject, body)
        if success:
            return

    # 2. Fallback to Resend API
    if RESEND_API_KEY:
        logger.info("Attempting to send forgot password email to %s via Resend...", receiver_email)
        try:
            resend.Emails.send(
                {
                    "from": FROM_EMAIL,
                    "to": receiver_email,
                    "subject": subject,
                    "text": body,
                }
            )
            logger.info("Forgot password OTP sent successfully to %s via Resend", receiver_email)
        except Exception as e:
            logger.error(
                "Failed to send password reset OTP to '%s' via Resend. Error: %s",
                receiver_email,
                e,
            )
    else:
        logger.error("No email delivery mechanism configured. Could not send email to %s", receiver_email)
