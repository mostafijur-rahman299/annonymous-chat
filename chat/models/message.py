from django.db import models
from chat.models import ChatRoom

class ChatMessage(models.Model):

    _STATUS = (
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('deleted', 'Deleted'),
    )

    # Link to the chat room
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=False, related_name="messages")
    
    # Sender and receiver identifiers (anonymous, no need for real numbers)
    sender_id = models.CharField(max_length=200, null=True, blank=True)  # Unique ID for sender
    # User's nickname for display purposes
    sender_nickname = models.CharField(max_length=255, null=True, blank=True)  # Display name for the sender
    sender_role = models.CharField(max_length=255, null=True, blank=True)  # Display name for the sender

    # Message content
    message_text = models.TextField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=255, default="delivered", choices=_STATUS)
       
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Message creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp

    def __str__(self):
        """String representation of the chat message."""
        return f"Message from {self.sender_id} in Room {self.room.room_code}"

