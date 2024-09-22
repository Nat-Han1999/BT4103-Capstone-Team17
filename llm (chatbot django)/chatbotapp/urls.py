from django.urls import path
from .views import send_message, list_messages, clear_messages

urlpatterns = [
    path('send', send_message, name='send_message'),
    path('clear_messages', clear_messages, name='clear_messages'),
    path('', list_messages, name='list_messages'),
]