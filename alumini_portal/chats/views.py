import json
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatRoom, Message
from adminpanel.models import Batch
from users.models import CustomUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden


@login_required
def chat_home_view(request):
    print(request.user.id)
    users = CustomUser.objects.exclude(Q(id=request.user.id) | Q(is_staff=True)|Q(is_alumini=True)) 
    return render(request, 'chats/chat_home.html', {'users': users})
class ChatRoomView(LoginRequiredMixin, View):
    def get(self, request, room_name):
        room = get_object_or_404(ChatRoom, name=room_name)

        # if request.user not in room.participants.all():
        #     return HttpResponseForbidden("You are not allowed to access this room.")

        messages = room.messages.select_related('sender').order_by('timestamp')

        return render(request, 'chats/chat_room.html', {
            'room': room,
            'messages': messages,
            'user': request.user
        })

class StartPrivateChatView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)

        if request.user.id == target_user.id:
            return HttpResponseBadRequest("You cannot chat with yourself.")

        # Generate unique room name
        user_ids = sorted([request.user.id, target_user.id])
        room_name = f"private_{user_ids[0]}_{user_ids[1]}"

        room, created = ChatRoom.objects.get_or_create(name=room_name, is_group=False)
        if not room.participants.filter(id=request.user.id).exists():
            room.participants.add(request.user)

        if not room.participants.filter(id=target_user.id).exists():
            room.participants.add(target_user)
        # Ensure both users are participants
        # room.participants.add(request.user)
        # room.participants.add(target_user)

        return redirect("chats:chat-room", room_name=room.name)

    
AVATAR_COLORS = ['#4caf50','#2196f3','#f44336','#ff9800','#9c27b0','#3f51b5','#009688','#e91e63','#607d8b','#795548']

class ChatWithAlumniListView(LoginRequiredMixin, TemplateView):
    template_name = "chats/chat_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        chat_rooms = ChatRoom.objects.filter(participants=user).prefetch_related("participants")

        visible_rooms = []
        for room in chat_rooms:
            room.other_participants = room.participants.exclude(
                Q(id=user.id) | Q(is_staff=True) | Q(is_superuser=True)
            )

            if not room.other_participants.exists():
                continue  

            first_user = room.other_participants.first()
            username = getattr(first_user.userdetails.first(), "firstname", "A") or "A"
            room.avatar_initial = username[0].upper()
            room.avatar_bg = AVATAR_COLORS[sum(ord(c) for c in username) % len(AVATAR_COLORS)]

            visible_rooms.append(room)

        context['chat_rooms'] = visible_rooms
        return context

class GroupChatRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.userdetails.first()
        print(profile)
        profile = getattr(request.user, "userdetails", None)
        if profile and profile.batch:
            batch = profile.batch
            room_name = f"group_batch_{batch.id}"
            room, _ = ChatRoom.objects.get_or_create(
                name=room_name,
                is_group=True,
                batch=batch
            )
            return redirect("chats:chat-room", room_name=room.name)



@method_decorator(csrf_exempt, name='dispatch') 
class SendMessageAPIView(LoginRequiredMixin, View):
    def post(self, request, room_name):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        room = get_object_or_404(ChatRoom, name=room_name)
        content = data.get("content")

        if not content:
            return JsonResponse({'error': 'No content provided'}, status=400)

        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content
        )
        return JsonResponse({
            "sender": request.user.get_full_name() or request.user.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        })
