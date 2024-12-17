import random
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat.models.room import ChatRoom


class CreateChatRoomView(APIView):
    def post(self, request, format=None):
        room_code = request.data.get('room_code')
        nickname = request.data.get('nickname')

        # Check if the room code is provided
        if room_code:
            # Check if the room code is already in use
            room = ChatRoom.objects.filter(room_code=room_code).first()
            if room:
                return Response({
                    "success": False, 
                    "message": "Room code already in use", 
                    "error": {
                        "room_code": "Room code already in use"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                room = ChatRoom.objects.create(room_code=room_code)

        # If no room code is provided, create a new room
        else:
            room = ChatRoom.objects.create()

        # Add the participant to the room

        # Generate unique user id
        user_id = uuid.uuid4()

        # Add the participant to the room
        room.add_participant(user_id, nickname)

        return Response({
            "success": True, 
            "message": "Room created successfully", 
            "data": {
                "room_code": room.room_code,
                "room_id": room.id
            }
        }, status=status.HTTP_201_CREATED)



class JoinChatRoomView(APIView):
    def post(self, request, format=None):
        room_code = request.data.get('room_code')
        nickname = request.data.get('nickname')

        # Check if the room code is provided
        if not room_code:
            return Response({
                "success": False, 
                "message": "Room code is required", 
                "error": {
                    "room_code": "Room code is required"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        room = ChatRoom.objects.filter(room_code=room_code, is_active=True).first()
        if not room:
            return Response({
                "success": False, 
                "message": "Room not found", 
                "error": {
                    "room_code": "Room not found"
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the room is private and already has 2 participants
        if room.is_private and len(room.participants) >= 2:
            return Response({
                "success": False, 
                "message": "Room is private and already has 2 participants", 
                "error": {
                    "room_code": "Room is private and already has 2 participants"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # If nickname is provided then check this would be unique for this room
        if nickname:
            if room.participants and nickname in room.participants.values():
                return Response({
                    "success": False, 
                    "message": "Nickname already in use", 
                    "error": {
                        "nickname": "Nickname already in use"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        if not nickname:
            nickname = f"Anonymous{random.randint(1000, 9999)}"

        # Add the participant to the room
        room.add_participant(request.user.id, nickname)

        return Response({
            "success": True, 
            "message": "Joined room successfully", 
            "data": {
                "room_code": room.room_code,
                "room_id": room.id,
                "nickname": nickname
            }
        }, status=status.HTTP_200_OK)

