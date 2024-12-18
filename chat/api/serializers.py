from rest_framework import serializers
from chat.models import ChatMessage

class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%H:%M:%S')

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_id', 'sender_nickname', 'message_text', 'created_at']
    
