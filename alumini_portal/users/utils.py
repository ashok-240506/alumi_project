
from twilio.rest import Client
from django.conf import settings


def has_role(user, role_name):
    print("Checking role for:", user)
    roles = user.user_role.all()
    print("User roles:", [r.role.role_name for r in roles])
    return user.user_role.filter(role__role_name__iexact=role_name).exists()

def send_otp_sms(to_number, otp_code):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP code is: {otp_code}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number 
    )
    return message.sid
