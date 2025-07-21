from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatRoom, Message
from adminpanel.models import Batch
from users.models import CustomUser

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def chat_home_view(request):
    return render(request, 'chats/chat_home.html')  # You can create this later

class ChatRoomView(LoginRequiredMixin, View):
    def get(self, request, room_name):
        room = get_object_or_404(ChatRoom, name=room_name)
        messages = room.messages.select_related('sender').order_by('timestamp')
        print(room,'-----------------')
        return render(request, 'chats/chat_room.html', {
            'room': room,
            'messages': messages,
            'user': request.user
        })


class StartPrivateChatView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)

        # Generate room name based on user IDs (always same order)
        user_ids = sorted([request.user.id, target_user.id])
        room_name = f"private_{user_ids[0]}_{user_ids[1]}"

        room, created = ChatRoom.objects.get_or_create(name=room_name, is_group=False)

        return redirect('chat-room', room_name=room.name)


class GroupChatRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        if hasattr(request.user, 'userpersonalprofile') and request.user.userpersonalprofile.batch:
            batch = request.user.userpersonalprofile.batch
            room_name = f"group_batch_{batch.id}"
            room, _ = ChatRoom.objects.get_or_create(
                name=room_name,
                is_group=True,
                batch=batch
            )
            return redirect('chat-room', room_name=room.name)
        return redirect('/')  # or error page
