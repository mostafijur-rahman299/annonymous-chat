from rest_framework import serializers
from chat.models import ChatMessage

class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%H:%M %p')
    sender = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'message_text', 'status', 'created_at']

    def get_sender(self, obj):
        return {
            "id": obj.sender_id,
            "nickname": obj.sender_nickname,
            "role": obj.sender_role
        }
    
