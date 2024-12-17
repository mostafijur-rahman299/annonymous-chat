from django.urls import path
from .views.chat_room import CreateChatRoomView, JoinChatRoomView

urlpatterns = [
    path('create-room/', CreateChatRoomView.as_view(), name='create_chat_room'),
    path('join-room/', JoinChatRoomView.as_view(), name='join_chat_room'),
]
