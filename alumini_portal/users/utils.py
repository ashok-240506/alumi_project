
from twilio.rest import Client
from django.conf import settings


def has_role(user, role_name):
    print("Checking role for:", user)
    roles = user.user_role.all()
    print("User roles:", [r.role.role_name for r in roles])
    return user.user_role.filter(role__role_name__iexact=role_name).exists()

OTP_TEMPLATE = "Dear {name}, your OTP for {purpose} is {otp}. Valid for 5 minutes."

def send_otp_sms(to_number, otp_code, name="User", purpose="login"):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
            body = OTP_TEMPLATE.format(name=name, purpose=purpose, otp=otp_code),
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number 
    )
    return message.sid
