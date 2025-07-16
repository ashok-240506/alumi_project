from django.urls import path
from .views import ChatRoomView, StartPrivateChatView, GroupChatRedirectView

urlpatterns = [
    path('room/<str:room_name>/', ChatRoomView.as_view(), name='chat-room'),
    path('private/<int:user_id>/', StartPrivateChatView.as_view(), name='start-private-chat'),
    path('group/', GroupChatRedirectView.as_view(), name='group-chat'),
]
