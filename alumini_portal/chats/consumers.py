# chats/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import localtime
from channels.db import database_sync_to_async
from .models import Message
# Async helper
@database_sync_to_async
def get_first_user_detail(user):
    return user.userdetails.first()
@database_sync_to_async
def save_message(room_id, sender, content):
    return Message.objects.create(room_id=room_id, sender=sender, content=content)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4001)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user = self.scope['user']

            msg_obj = await save_message(self.room_name, user, data['message'])

            user_detail = await database_sync_to_async(lambda: user.userdetails.first())()
            username = user_detail.get_full_name() if user_detail else str(user)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": msg_obj.content,
                    "username": username,
                    "timestamp": str(msg_obj.timestamp),
                    "id": msg_obj.id
                }
            )
        except Exception as e:
            print("Error in receive:", e)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, content):
        from .models import ChatRoom, Message 
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=user, content=content)
