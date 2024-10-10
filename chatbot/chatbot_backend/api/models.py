# api/models.py

from django.db import models
import uuid


class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Conversation {self.conversation_id} started at {self.started_at}"

class Message(models.Model):
    sender = models.CharField(max_length=10)  # 'User' or 'Bot'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.timestamp} - {self.sender}: {self.text}"
