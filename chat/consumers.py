import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, ChatMessage
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the room_code from the URL
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'chat_{self.room_code}'

        # Check if the room exists, if not, create it
        room, created = await sync_to_async(ChatRoom.objects.get_or_create)(room_code=self.room_code)

        # Add the user to the chat room participants
        self.user_id = str(self.channel_name)  # You can use a unique ID for each user
        self.nickname = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonymous'
        await sync_to_async(room.add_participant)(self.user_id, self.nickname)

        # Join the room group (WebSocket broadcast group)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from the room group
        room = await sync_to_async(ChatRoom.objects.get)(room_code=self.room_code)
        await sync_to_async(room.remove_participant)(self.user_id)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        
        # Store the message in the database
        room = await sync_to_async(ChatRoom.objects.get)(room_code=self.room_code)
        message = await sync_to_async(ChatMessage.objects.create)(
            room=room,
            sender_id=self.user_id,
            sender_nickname=self.nickname,
            message_text=message_text
        )

        # Send the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.message_text,
                'sender': self.nickname
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
