from datetime import timedelta, timezone
from django.db import models
from utils.custom_func import generate_random_string
from django.utils.timesince import timesince

class ChatRoom(models.Model):

    # Participants Format: {
    #     "participant_id": {
    #         "nickname": "nickname",
    #         "role": "host" | "guest"
    #     }
    # }

    expiration_duration_unit_options = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
    ]

    # Unique identifier for the chat room
    room_code = models.CharField(max_length=200, unique=True, null=True, blank=True)  # Unique room code
    participants = models.JSONField(null=True, blank=True)  # Store participant identifiers and their nicknames
    created_at = models.DateTimeField(auto_now_add=True)  # When the chat room was created
    is_active = models.BooleanField(default=True)  # Marks if the chat room is still active
    max_participants = models.IntegerField(default=10)  # Maximum number of participants in the room
    expiration_time = models.DateTimeField(null=True, blank=True)  # When the chat room expires
    expiration_duration = models.IntegerField(default=5)  # Duration in minutes
    expiration_duration_unit = models.CharField(max_length=20, default="minutes", choices=expiration_duration_unit_options)  # Unit of duration
    

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
        if self.participants and participant_id in self.participants:
            self.participants[participant_id]["nickname"] = nickname
            self.save()

    def set_expiration_time(self):
        # Set the expiration time based on the duration and unit
        if self.expiration_duration and self.expiration_duration_unit:
            duration = self.expiration_duration
            unit = self.expiration_duration_unit
            if unit == 'minutes':
                self.expiration_time = timezone.now() + timedelta(minutes=duration)
            elif unit == 'hours':
                self.expiration_time = timezone.now() + timedelta(hours=duration)
            elif unit == 'days':
                self.expiration_time = timezone.now() + timedelta(days=duration)
            self.save()

    def is_expired(self):
        if self.expiration_time and timezone.now() > self.expiration_time:
            self.is_active = False
            self.save()
            return True
        return False

    def get_expiration_time(self):
        if self.expiration_time:
            delta = self.expiration_time - timezone.now()
            if delta.total_seconds() > 0:
                return f"{delta.days} days, {delta.seconds // 3600} hours remaining"
            return "Expired"
        return "No expiration set"
