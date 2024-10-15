from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models_mongo import ChatSession, Message
import torch
import uuid
from datetime import datetime, timezone
from decouple import config
import google.generativeai as genai

#Gemni setup
GENERATIVE_AI_KEY = config('GOOGLE_GENERATIVE_AI_KEY')
genai.configure(api_key=GENERATIVE_AI_KEY)


@api_view(['POST'])
def generate_response(request):
    try:
        prompt = request.data.get('prompt', '')
        conversation_id = request.data.get('conversation_id', None)

        if not prompt:
            return Response({'error': 'No prompt provided.'}, status=400)

        # Retrieve or create the chat session
        if conversation_id:
            # Try to get the existing conversation
            chat_session = ChatSession.objects(session_id=uuid.UUID(conversation_id)).first()
            if not chat_session:
                # If not found, create a new session
                chat_session = ChatSession(session_id=uuid.UUID(conversation_id))
        else:
            # Create a new conversation
            chat_session = ChatSession()
            conversation_id = str(chat_session.session_id)

        # Save user's message
        user_message = Message(
            sender='User',
            text=prompt,
            timestamp=datetime.now(timezone.utc)
        )
        chat_session.messages.append(user_message)

        # Use Google's Gemini model
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Prepare the conversation history if needed
        conversation_history = ''
        for msg in chat_session.messages:
            conversation_history += f"{msg.sender}: {msg.text}\n"

        full_prompt = conversation_history + "Bot:"

        # Generate the response
        bot_response = model.generate_content(full_prompt)
        response_text = bot_response.text.strip()

        # Save bot's response
        bot_message = Message(
            sender='Bot',
            text=response_text,
            timestamp=datetime.now(timezone.utc)
        )
        chat_session.messages.append(bot_message)

        # Save the chat session
        chat_session.save()

        return Response({
            'response': response_text,
            'conversation_id': conversation_id
        })
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)

@api_view(['POST'])
def submit_feedback(request):
    try:
        conversation_id = request.data.get('conversation_id', None)
        message_id = request.data.get('message_id', None)
        feedback = request.data.get('feedback', None)

        if not all([conversation_id, message_id, feedback]):
            return Response({'error': 'Missing parameters.'}, status=400)

        chat_session = ChatSession.objects(session_id=uuid.UUID(conversation_id)).first()
        if not chat_session:
            return Response({'error': 'Conversation not found.'}, status=404)

        # Find the message in the chat session
        message = next((msg for msg in chat_session.messages if str(msg.id) == message_id), None)
        if not message:
            return Response({'error': 'Message not found.'}, status=404)

        # Save feedback in the message
        message.feedback = feedback
        chat_session.save()

        return Response({'status': 'Feedback received.'})
    except Exception as e:
        print(f"Error in submit_feedback: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)

@api_view(['GET'])
def get_conversation(request, conversation_id):
    try:
        chat_session = ChatSession.objects(session_id=uuid.UUID(str(conversation_id))).first()
        if not chat_session:
            return Response({'error': 'Conversation not found.'}, status=404)

        messages = [
            {
                'id': str(msg.id),
                'sender': msg.sender,
                'text': msg.text,
                'timestamp': msg.timestamp.isoformat(),
                'feedback': msg.feedback,  # Include feedback
            }
            for msg in chat_session.messages
        ]
        return Response({'messages': messages})
    except Exception as e:
        print(f"Error in get_conversation: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)