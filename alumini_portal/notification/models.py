from django.db import models
from users.models import *

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)  
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender_notification",null=True,blank=True)

    class Meta:
        db_table = 'notification'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"