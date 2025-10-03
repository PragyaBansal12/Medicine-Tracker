from pywebpush import webpush
from django.conf import settings

def send_web_push(subscription_info, message):
    """Send a web push notification to a specific subscription"""
    webpush(
        subscription_info=subscription_info,
        data=message,
        vapid_private_key=settings.VAPID_PRIVATE_KEY,
        vapid_claims={"sub": "mailto:medication-tracker@example.com"}
    )
