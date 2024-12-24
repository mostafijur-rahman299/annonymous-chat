import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, ChatMessage
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the room_code from the URL
        room_code = self.scope['url_route']['kwargs']['room_code']
        self.participant_id = self.scope['query_string'].decode('utf-8').split('=')[1]
        self.room_group_name = f'chat_{room_code}'

        # Check if the room exists, if not, create it
        try:
            self.room = await sync_to_async(ChatRoom.objects.get)(room_code=room_code)
        except ChatRoom.DoesNotExist:
            print("Room not found")
            self.send({
                'type': 'error',
                'error': 'Room not found'
            })
            return
        except Exception as e:
            self.send({
                'type': 'error',
                'error': 'Internal server error'
            })
            return
        
        # Find the sender
        self.participant = self.room.participants.get(self.participant_id)
        if not self.participant:
            self.send({
                'type': 'error',
                'error': 'You are not a participant of this room'
            })
            return
        
        # Add the user to the chat room participants
        self.user_id = str(self.channel_name)  # You can use a unique ID for each user

        # Join the room group (WebSocket broadcast group)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']

        if command == 'send_message':
            message_text = text_data_json['message']
            message_tmp_id = text_data_json['message_tmp_id']
            
            message = await sync_to_async(ChatMessage.objects.create)(
                room=self.room,
                sender_id=self.participant_id,
                sender_nickname=self.participant.get("nickname"),
                sender_role=self.participant.get("role"),
                message_text=message_text
            )

            # Send the message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_message',
                    'message': {
                        'id': message.id,
                        'message_tmp_id': message_tmp_id,
                        'message_text': message.message_text,
                        'created_at': message.created_at.strftime(
                            "%H:%M:%S %p"
                        ),
                        'status': message.status
                    },
                    'sender': { 
                        'id': self.participant_id,
                        'nickname': self.participant.get("nickname"),
                        'role': self.participant.get("role")
                    }
                }
            )
        elif command == 'leave_room':
            participant = self.room.participants.get(self.participant_id)
            if participant.get("role") == "host":
                await sync_to_async(self.room.delete)()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'host_dismiss_room'
                    }
                )
            else:
                await sync_to_async(self.room.remove_participant)(self.participant_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'participant_toggled',
                        'response_type': 'leave_participant',
                        'participant': {
                            'participant_id': self.participant_id,
                            'nickname': self.participant.get("nickname"),
                            'role': self.participant.get("role")
                        }
                    }
                )


    # Receive message from room group
    async def new_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'response_type': 'new_message',
            'id': message['id'],
            'message_tmp_id': message['message_tmp_id'],
            'message_text': message['message_text'],
            'created_at': message['created_at'],
            'sender': sender,
            'status': message['status']
        }))

    async def host_dismiss_room(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'host_dismiss_room'
        }))

    async def error(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'error',
            'error': event['error']
        }))

    async def participant_toggled(self, event):
        await self.send(text_data=json.dumps({
            'response_type': event['response_type'],
            'participant': event['participant']
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
