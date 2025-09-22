from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from users.models import CustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_all_alumni(job, posted_by):
    users = CustomUser.objects.filter(is_alumini=True,is_staff=False,is_active=True).exclude(id=posted_by.id)
    sender = CustomUser.objects.filter(id=posted_by.id,is_alumini=True,is_staff=False,is_active=True).first()
    channel_layer = get_channel_layer()

    for user in users:
        Notification.objects.create(
            recipient=user,
            created_by=sender,
            title="New Job Posted",
            message=f"{job.title} - {job.description[:100]}...",
            url=f"/jobs/{job.id}/"
        )

        # Email Notification
        if user.email:
            send_mail(
                subject=f"New Job: {job.title}",
                message=f"A new job has been posted.\n\n{job.description}\n\nView: http://127.0.0.1:8000/jobs/{job.id}/",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        # Real-time Push via WebSocket
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "content": {
                    "title": "New Job Posted",
                    "message": f"{job.title} - {job.description[:50]}...",
                    "url": f"http://127.0.0.1:8000/jobs/{job.id}/"
                }
            }
        )
