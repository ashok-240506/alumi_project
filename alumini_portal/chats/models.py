from django.db import models
from django.conf import settings
from adminpanel.models import Batch

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_group = models.BooleanField(default=False)
    batch = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.SET_NULL)  # For group chat\
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chat_rooms", blank=True)


    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.room.name}: {self.content[:30]}"
