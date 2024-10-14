import uuid
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

class Message(EmbeddedDocument):
    sender = fields.StringField(required=True, max_length=10)  # 'User' or 'Bot'
    text = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True, default=datetime.utcnow)

class ChatSession(Document):
    session_id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = fields.DateTimeField(required=True, default=datetime.utcnow)
    messages = fields.EmbeddedDocumentListField(Message)
    meta = {'collection': 'chat_sessions'}