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
from django.utils.timezone import localtime
from django.views.decorators.clickjacking import xframe_options_exempt
@login_required
def chat_home_view(request):
    print(request.user.id)
    users = CustomUser.objects.exclude(Q(id=request.user.id) | Q(is_staff=True)|Q(is_alumini=True)) 
    return render(request, 'chats/chat_home.html', {'users': users})
class ChatRoomView(LoginRequiredMixin, View):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        room.messages.filter(
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)

        messages = room.messages.select_related('sender').order_by('timestamp')

        other_user = None
        if not room.is_group:
            other_user = room.participants.exclude(id=request.user.id).first()

        return render(request, 'chats/chat_room.html', {
            'room': room,
            'messages': messages,
            'user': request.user,
            'other_user': other_user
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
        room.participants.add(request.user, target_user)

        return redirect("chats:chat-room", room_id=room.id)


    
AVATAR_COLORS = ['#4caf50','#2196f3','#f44336','#ff9800','#9c27b0','#3f51b5','#009688','#e91e63','#607d8b','#795548']

class ChatWithAlumniListView(LoginRequiredMixin, TemplateView):
    template_name = "chats/chat_home.html"

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

            profile = first_user.userdetails.first()
            if profile and profile.full_name:
                room.display_name = profile.full_name
            else:
                room.display_name = first_user.get_full_name() or first_user.username

            initial_char = room.display_name[0].upper()
            room.avatar_initial = initial_char
            room.avatar_bg = AVATAR_COLORS[sum(ord(c) for c in initial_char) % len(AVATAR_COLORS)]
            last_msg = room.messages.order_by("-timestamp").first()
            room.last_message = last_msg
            room.last_message_time = last_msg.timestamp if last_msg else None

            print(room.last_message_time)
            room.unread_count = room.messages.filter(
                    is_read=False
                ).exclude(sender=user).count()


            visible_rooms.append(room)

        context['chat_rooms'] = visible_rooms
        context["details"] = user.userdetails.first()  
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


class SendMessageAPIView(LoginRequiredMixin, View):
    def post(self, request, room_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        room = get_object_or_404(ChatRoom, id=room_id)
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

@xframe_options_exempt
def chatbot_view(request):
    return render(request, "chats/chatbot.html")
@login_required
def chat_messages_api(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.select_related('sender').order_by('timestamp')
    data = [{
        'sender_name': m.sender.get_full_name() or m.sender.username,
        'content': m.content,
        'timestamp': m.timestamp.isoformat(),
        'is_sender': m.sender == request.user
    } for m in messages]
    return JsonResponse({'messages': data})

class ChatHistoryView(LoginRequiredMixin, View):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

        messages = Message.objects.filter(room=room).select_related("sender").order_by("timestamp")
        
        data = []
        for m in messages:
            user_detail = m.sender.userdetails.first()
            if user_detail:
                username = f"{user_detail.firstname} {user_detail.lastname}"
            else:
                username = str(m.sender)  # fallback if profile missing

            data.append({
                "id": m.id,
                "username": username,
                "message": m.content,
                "timestamp": m.timestamp.isoformat(),
            })

        return JsonResponse(data, safe=False)

class GetOrCreateChatRoomView(LoginRequiredMixin, View):
    def get(self, request, alumini_id):
        target_user = get_object_or_404(CustomUser, id=alumini_id)

        room = ChatRoom.objects.filter(is_group=False, participants=request.user)\
                               .filter(participants=target_user).first()
        if not room:
            user_ids = sorted([request.user.id, target_user.id])
            room_name = f"room_{user_ids[0]}_{user_ids[1]}"

            room = ChatRoom.objects.create(name=room_name, is_group=False)
            room.participants.add(request.user, target_user)

        profile = target_user.userdetails.first() if hasattr(target_user, "userdetails") else None
        display_name = profile.full_name if profile and profile.full_name else target_user.get_full_name() or target_user.username

        return JsonResponse({"room_id": room.id, "display_name": display_name})
