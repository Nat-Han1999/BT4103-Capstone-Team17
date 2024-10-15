import uuid
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime, timezone

class Message(EmbeddedDocument):
    id = fields.UUIDField(required=True, default=uuid.uuid4)
    sender = fields.StringField(required=True, max_length=10)  # 'User' or 'Bot'
    text = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True, default=lambda: datetime.now(timezone.utc))
    feedback = fields.StringField(choices=['like', 'dislike'], null=True)

class ChatSession(Document):
    session_id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = fields.DateTimeField(required=True, default=lambda: datetime.now(timezone.utc))
    messages = fields.EmbeddedDocumentListField(Message)
    meta = {'collection': 'chat_sessions'}