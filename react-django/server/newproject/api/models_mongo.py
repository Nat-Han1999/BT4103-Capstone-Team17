import uuid
from mongoengine import Document, EmbeddedDocument, fields, DynamicDocument
from datetime import datetime, timezone

class Message(EmbeddedDocument):
    id = fields.IntField(required=True)
    sender = fields.StringField(required=True, max_length=10)  # 'User' or 'Bot'
    text = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True, default=lambda: datetime.now(timezone.utc))
    feedback = fields.StringField(choices=['like', 'dislike'], null=True)

class ChatSession(Document):
    session_id = fields.UUIDField(primary_key=True)
    started_at = fields.DateTimeField(required=True, default=lambda: datetime.now(timezone.utc))
    messages = fields.EmbeddedDocumentListField(Message)
    avatarSelected = fields.StringField(required=True, default="Helen")
    backgroundSelected = fields.StringField(required=True, default="avatar_bg")
    meta = {'collection': 'chat_sessions'}

class ScrapedData(DynamicDocument):
    meta = {'collection':'scraped_data'}