import os
from app.alerts.email_alert import EmailAlertSender
from app.data.models import Violation

sender = EmailAlertSender(
    sender_address=os.environ["GMAIL_ADDRESS"],
    app_password=os.environ["GMAIL_APP_PASSWORD"],
    recipients=[os.environ["GMAIL_ADDRESS"]],  # send to yourself for this test
)

test_violation = Violation(
    camera_id="cam-yard-01", zone="yard", violation_class="NO-Hardhat",
    snapshot_path="cam-yard-01/2026-08-08/1786200098.jpg",
    snapshot_hash="fe110b1e...", confidence=0.38,
)

sender.send_violation_alert(test_violation)
print("Alert email sent - check your inbox")