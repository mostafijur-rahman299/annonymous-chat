from django.db import models
from utils.custom_func import generate_random_string


class ChatRoom(models.Model):

    # Participants Format: {
    #     "participant_id": {
    #         "nickname": "nickname",
    #         "role": "host" | "guest"
    #     }
    # }

    # Unique identifier for the chat room
    room_code = models.CharField(max_length=10, unique=True, null=True, blank=True)  # Unique room code
    participants = models.JSONField(null=True, blank=True)  # Store participant identifiers and their nicknames
    created_at = models.DateTimeField(auto_now_add=True)  # When the chat room was created
    is_active = models.BooleanField(default=True)  # Marks if the chat room is still active
    max_participants = models.IntegerField(default=2)  # Maximum number of participants in the room

    def __str__(self):
        return f"Room: {self.room_code}"

    def save(self, *args, **kwargs):
        # Ensure unique room code generation on save
        if not self.room_code:
            self.room_code = generate_random_string(length=10)  # Generate random code with desired length
            while ChatRoom.objects.filter(room_code__iexact=self.room_code).exists():
                self.room_code = generate_random_string(length=10)  # Regenerate if the code already exists
        super().save(*args, **kwargs)

    def add_participant(self, participant_id, nickname, role="guest"):
        # Add participant ID with their nickname to the participants list
        if self.participants is None:
            self.participants = {}
        if participant_id not in self.participants:
            self.participants[participant_id] = {
                "nickname": nickname or "Anonymous",
                "role": role
            }
            self.save()

    def remove_participant(self, participant_id):
        # Remove participant from the room
        if self.participants and participant_id in self.participants:
            del self.participants[participant_id]
            self.save()

    def update_nickname(self, participant_id, nickname):
        # Update the nickname for an existing participant
        if self.participants and participant_id in self.participants:
            self.participants[participant_id] = nickname
            self.save()
