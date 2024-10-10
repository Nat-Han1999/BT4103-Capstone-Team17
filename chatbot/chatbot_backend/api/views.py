# api/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from transformers import AutoModelForCausalLM, AutoTokenizer
from .models import Message, Conversation
import torch
import uuid

# Device setup
if torch.cuda.is_available():
    device = torch.device('cuda')
elif torch.backends.mps.is_available():
    device = torch.device('mps')
else:
    device = torch.device('cpu')

# Preload models and tokenizers
model_names = ['distilgpt2', 'gpt2']  # Add more model names if needed
models = {}
tokenizers = {}

for name in model_names:
    tokenizers[name] = AutoTokenizer.from_pretrained(name)
    models[name] = AutoModelForCausalLM.from_pretrained(name)
    models[name].to(device)
    models[name].eval()

@api_view(['POST'])
def generate_response(request):
    try:
        prompt = request.data.get('prompt', '')
        conversation_id = request.data.get('conversation_id', None)
        model_name = request.data.get('model_name', 'distilgpt2')

        if not prompt:
            return Response({'error': 'No prompt provided.'}, status=400)

        if model_name not in models:
            return Response({'error': f'Model "{model_name}" is not available.'}, status=400)

        # Retrieve or create the conversation
        if conversation_id:
            # Try to get the existing conversation
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
            except Conversation.DoesNotExist:
                # If not found, create a new conversation
                conversation = Conversation.objects.create()
                conversation_id = str(conversation.conversation_id)
        else:
            # Create a new conversation
            conversation = Conversation.objects.create()
            conversation_id = str(conversation.conversation_id)

        # Save user's message
        Message.objects.create(sender='User', text=prompt, conversation=conversation)

        tokenizer = tokenizers[model_name]
        model = models[model_name]

        inputs = tokenizer(prompt, return_tensors='pt').to(device)

        # Generate text
        outputs = model.generate(
            **inputs,
            max_length=150,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            early_stopping=True,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=inputs['attention_mask'],
        )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = generated_text[len(prompt):].strip()

        # Save bot's response
        Message.objects.create(sender='Bot', text=response_text, conversation=conversation)

        return Response({
            'response': response_text,
            'conversation_id': conversation_id
        })
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)
    
#Add a new view to fetch messages based on conversation_id.
@api_view(['GET'])
def get_conversation(request, conversation_id):
    messages = Message.objects.filter(conversation_id=conversation_id).order_by('timestamp')
    message_data = [{'sender': msg.sender, 'text': msg.text} for msg in messages]
    return Response({'messages': message_data})