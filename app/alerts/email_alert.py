import smtplib
import ssl
from email.message import EmailMessage
from typing import List

from app.data.models import Violation

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


class EmailAlertSender:
    def __init__(self, sender_address: str, app_password: str, recipients: List[str]):
        self.sender_address = sender_address
        self.app_password = app_password
        self.recipients = recipients

    def send_violation_alert(self, violation: Violation) -> None:
        """Build and send one alert email for a single violation."""
        message = self._build_message(violation)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(self.sender_address, self.app_password)
            server.send_message(message)

    def _build_message(self, violation: Violation) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = f"PPE Violation: {violation.violation_class} - {violation.zone}"
        message["From"] = self.sender_address
        message["To"] = ", ".join(self.recipients)
        message.set_content(
            f"A PPE violation was detected.\n\n"
            f"Camera: {violation.camera_id}\n"
            f"Zone: {violation.zone}\n"
            f"Type: {violation.violation_class}\n"
            f"Time (UTC): {violation.timestamp}\n"
            f"Confidence: {violation.confidence}\n"
            f"Evidence file: {violation.snapshot_path}\n"
        )
        return message