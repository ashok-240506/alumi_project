from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job
from notification.utils import notify_all_alumni

@receiver(post_save, sender=Job)
def job_posted_notification(sender, instance, created, **kwargs):
    print(created)
    if created:
        notify_all_alumni(instance, instance.posted_by)
