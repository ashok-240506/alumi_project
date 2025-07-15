from django.core.management.base import BaseCommand
from users.models import OTP
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete expired OTPs'

    def handle(self, *args, **kwargs):
        expiry_time = timezone.now() - timedelta(minutes=10)
        deleted, _ = OTP.objects.filter(created_at__lt=expiry_time).delete()
        self.stdout.write(f"Deleted {deleted} expired OTPs.")
