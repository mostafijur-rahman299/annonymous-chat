import pytz
from django.utils import timezone
from rest_framework import serializers
from chat.models import ChatMessage

class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
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

    def get_created_at(self, obj):
        # Get the desired timezone from the context
        desired_timezone = self.context.get("timezone", None)

        # Ensure that the 'created_at' is timezone-aware before converting
        if obj.created_at and timezone.is_aware(obj.created_at):
            if desired_timezone:
                # Convert the timestamp to the desired timezone using pytz
                try:
                    tz = pytz.timezone(desired_timezone)  # Use pytz to get the timezone
                    localized_time = obj.created_at.astimezone(tz)  # Convert to the desired timezone
                    return localized_time.strftime('%I:%M %p')  # Return formatted time (12-hour AM/PM)
                except pytz.UnknownTimeZoneError:
                    return obj.created_at.strftime('%I:%M %p')  # Return default formatted time if invalid timezone
            else:
                # If no desired timezone is passed, return the time in the default timezone
                return obj.created_at.strftime('%I:%M %p')

        return None  # If 'created_at' is missing or naive, return None
