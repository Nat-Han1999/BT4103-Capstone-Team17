from django.contrib import admin

# Register your models here.
# api/admin.py

# api/admin.py
from .models import Message, Conversation

admin.site.register(Message)
admin.site.register(Conversation)

