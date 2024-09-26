from django.shortcuts import render, redirect
from chatbot.settings import GENERATIVE_AI_KEY
from chatbotapp.models import ChatMessage
import google.generativeai as genai

def send_message(request):
    if request.method == 'POST':
        genai.configure(api_key=GENERATIVE_AI_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")

        user_message = request.POST.get('user_message')
        bot_response = model.generate_content(user_message)

        ChatMessage.objects.create(user_message=user_message, bot_response=bot_response.text)

    return redirect('list_messages')

def list_messages(request):
    messages = ChatMessage.objects.all()
    return render(request, 'chatbot/list_messages.html', { 'messages': messages })

def clear_messages(request):
    if request.method == 'POST':
        # Delete all chat messages from the database
        ChatMessage.objects.all().delete()
    return redirect('list_messages')
