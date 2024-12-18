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
        participant_id = random.randint(1000000000, 9999999999)
        room.save()

        # Add the participant to the room
        room.add_participant(participant_id, nickname, "host")

        return Response({
            "success": True,
            "message": "Room created successfully", 
            "data": {
                "room_code": room.room_code,
                "participant_id": participant_id,
                "nickname": room.participants[participant_id]["nickname"]
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
        if len(room.participants) >= room.max_participants:
            return Response({
                "success": False, 
                "message": f"Room is full", 
                "error": {
                    "room_code": f"Room is full"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # If nickname is provided then check this would be unique for this room
        if nickname:
            # Check if the nickname is already in use
            nicknames = [participant["nickname"].lower() for participant in room.participants.values()]
            if nickname.lower() in nicknames:

                # Generate a suggested nickname
                suggested_nickname = f"{nickname}{random.randint(1000, 9999)}"
                while suggested_nickname.lower() in nicknames:
                    suggested_nickname = f"{nickname}{random.randint(1000, 9999)}"

                return Response({
                    "success": False, 
                    "message": "Nickname already in use", 
                    "error": {
                        "nickname": "Nickname already in use. Please try a different nickname. Suggested nickname: " + suggested_nickname
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        if not nickname:
            nickname = f"Anonymous{random.randint(1000, 9999)}"

        # Check if the room is full
        if len(room.participants) >= room.max_participants:
            return Response({
                "success": False, 
                "message": f"Room is private and already has {room.max_participants} participants", 
                "error": {
                    "room_code": f"Room is private and already has {room.max_participants} participants"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Add the participant to the room
        participant_id = random.randint(1000000000, 9999999999)
        while room.participants.get(participant_id):
            participant_id = random.randint(1000000000, 9999999999)

        room.add_participant(participant_id, nickname)

        return Response({
            "success": True, 
            "message": "Joined room successfully", 
            "data": {
                "room_code": room.room_code,
                "room_id": room.id,
                "nickname": nickname
            }
        }, status=status.HTTP_200_OK)


class ParticipantList(APIView):
    def get(self, request, room_code, format=None):
        room = ChatRoom.objects.filter(room_code=room_code).first()
        participants = room.participants
        return Response(participants, status=status.HTTP_200_OK)
