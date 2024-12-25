from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat.api.serializers import MessageSerializer
from chat.models import ChatMessage

class MessageList(APIView):
    def get(self, request, room_code, format=None):
        timezone = request.GET.get('timezone', None)
        messages = ChatMessage.objects.filter(room__room_code=room_code)
        serializer = MessageSerializer(messages, many=True, context={'timezone': timezone})
        return Response(serializer.data, status=status.HTTP_200_OK)
