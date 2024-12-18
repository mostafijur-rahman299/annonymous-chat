from django.urls import path
from .views.room import CreateChatRoomView, JoinChatRoomView, ParticipantList
from .views.message import MessageList

urlpatterns = [
    path('create-room/', CreateChatRoomView.as_view(), name='create_chat_room'),
    path('join-room/', JoinChatRoomView.as_view(), name='join_chat_room'),
    path('room-participants/<str:room_code>/', ParticipantList.as_view(), name='participant_list'),
    path('room-messages/<str:room_code>/', MessageList.as_view(), name='message_list'),
]
