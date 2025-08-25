from django.urls import path
from .views import *
app_name = 'chats'

urlpatterns = [
    path('', chat_home_view, name='chat_home'),
    path('room/<int:room_id>/', ChatRoomView.as_view(), name='chat-room'),
    path('private/<int:user_id>/', StartPrivateChatView.as_view(), name='start-private-chat'),
    path('group/', GroupChatRedirectView.as_view(), name='group-chat-redirect'),
    path('send-message/<str:room_name>/', SendMessageAPIView.as_view(), name='send-message-api'),
    path('chat/alumni/', ChatWithAlumniListView.as_view(), name='chat_with_alumni'),
    path("chatbot/", chatbot_view, name="chatbot"),


]
