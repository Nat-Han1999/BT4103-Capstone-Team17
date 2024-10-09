import json
import numpy as np
import google.generativeai as genai
from chatbot.settings import GENERATIVE_AI_KEY
from chatbotapp.models import ChatMessage
from django.shortcuts import render, redirect
from django.conf import settings
from django.db.models import Max
import os
import textwrap
import string

# Load data during app initialization or as cache
data_path = '../scraper/scraped_data/data_requests.json'
genai.configure(api_key=GENERATIVE_AI_KEY)
with open(data_path, 'r') as file:
    data = json.load(file)

def process_data(data):
    cleaned_data = {}
    for item in data:
        cleaned_title = ''
        for (key, value) in item.items():
            if key == 'title':
                cleaned_title = value
                break
        item['texts'] = item['texts'] + item['image_extracted']
        cleaned_data[cleaned_title] = item

    # Combine cleaned texts
    training_data = []

    for page_title, data in cleaned_data.items():
        training_data.append({
            'title': page_title,
            'texts': data['texts'],
        })
    
    return training_data


# Function to split long texts into chunks of up to 9,000 characters
def split_text(text, max_chars=9000):
    print(f"Original text length: {len(text)} characters")  # Debug: Print original length
    
    parts = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    
    for i, part in enumerate(parts):
        print(f"Chunk {i+1} length: {len(part)} characters")  # Debug: Print chunk length
    
    return parts

# Function to embed content
def embed_fn(title, text):
    model = 'models/text-embedding-004'
    return genai.embed_content(model=model,
                               content=text,
                               task_type="retrieval_document",
                               title=title)["embedding"]

# Embed the cleaned training data
def generate_embeddings(training_data):
    for item in training_data:
        text = item['texts']
        if len(text) > 9000:
            # Split large texts and embed each chunk
            text_chunks = split_text(text)
            embeddings = [embed_fn(item['title'], chunk) for chunk in text_chunks]
            item['embedding'] = embeddings  # Store aggregated embedding
        else:
            # If the text is small enough, embed directly
            item['embedding'] = embed_fn(item['title'], text)
    return training_data

cleaned_training_data = process_data(data)
training_data = generate_embeddings(cleaned_training_data)

# Function to find the best passage based on embeddings
def find_best_passage(query, training_data):
    query_embedding = genai.embed_content(model='models/text-embedding-004',
                                          content=query,
                                          task_type="retrieval_query")['embedding']
    
    best_score = -float('inf')  # Initialize best score as negative infinity
    best_passage = None  # Variable to hold the best passage text

    # Iterate through each document's embeddings
    for item in training_data:
        embeddings = item['embedding']  # This can be a single embedding or a list of embeddings

        # If the document has multiple embeddings (from splitting)
        if len(embeddings) > 1:
            # Compute the dot product for each chunk and find the best chunk
            for embedding in embeddings:
                score = np.dot(embedding, query_embedding).sum()
                if score > best_score:
                    best_score = score
                    best_passage = item['texts']  # Return the whole document's text
        else:
            # If it's a single embedding
            score = np.dot(embeddings, query_embedding)
            if score > best_score:
                best_score = score
                best_passage = item['texts']

    return best_passage

# Function to create prompt based on query and relevant passage
def make_prompt(query, relevant_passage, convo_history):
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    prompt = textwrap.dedent(f"""\
    You are a helpful and informative bot that answers questions using text from the reference passage included below. \
    The term 'the fund' in any question should refers to the Shrama Vasana Fund.\
    Please answer to the best of your ability. Do not mention the context to your audience, just answer their questions.\
    Be sure to respond in complete sentences and break them into succinct paragraphs and bulletpoints for readability.\
    Please be comprehensive and include all relevant background information. \
    If the passage is irrelevant to the answer, you may ignore it.

    PREVIOUS CONVERSATION: '{convo_history}'                         
    QUESTION: '{query}'
    PASSAGE: '{escaped}'

    ANSWER:
    """)
    
    return prompt

def send_message(request):
    if request.method == 'POST':
        genai.configure(api_key=GENERATIVE_AI_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Get or create the conversation_id
        conversation_id = request.session.get('conversation_id', None)
        if not conversation_id:
            # Check if ChatMessage table has any records
            last_message = ChatMessage.objects.aggregate(Max('id'))
            if last_message['id__max'] is None:
                # No existing messages, start with conversation_id = 1
                conversation_id = 1
            else:
                # Increment from the latest id
                conversation_id = last_message['id__max'] + 1

            request.session['conversation_id'] = conversation_id

        user_message = request.POST.get('user_message')

        # Retrieve previous prompts and responses (limit to last 5 for brevity)
        convo_history = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('-id')[:5]
        
         # Find the best passage based on embeddings
        relevant_passage = find_best_passage(user_message, training_data)

        # Create the prompt using the relevant passage
        prompt = make_prompt(user_message, relevant_passage, convo_history)

        bot_response = model.generate_content(prompt)

        ChatMessage.objects.create(
            conversation_id=conversation_id,
            user_message=user_message, 
            bot_response=bot_response.text
        )

    return redirect('list_messages')

def list_messages(request):
    messages = ChatMessage.objects.all()
    return render(request, 'chatbot/list_messages.html', { 'messages': messages })

def clear_messages(request):
    if request.method == 'POST':
        # Delete all chat messages from the database
        ChatMessage.objects.all().delete()
    return redirect('list_messages')
