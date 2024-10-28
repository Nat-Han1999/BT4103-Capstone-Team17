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
import time
import re
import textstat
from statistics import mean, median
import markdown
from django.core.management import call_command
from django.http import HttpRequest
from django.core.signals import request_finished
from .test_cases import tests

from .mongo_utils import get_database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("MONGO_DB_USERNAME")
password = os.getenv("MONGO_DB_PASSWORD")
collection_scraped_data = get_database("shrama_vasana_fund", "scraped_data", username, password)

documents = collection_scraped_data.find()
genai.configure(api_key=GENERATIVE_AI_KEY)

# Load data during app initialization or as cache
# data_path = '../scraper/scraped_data/scraped_data.json'

# with open(data_path, 'r') as file:
#     data = json.load(file)


def process_data(data):
    cleaned_data = {}
    for item in data:
        if 'title' in item:
            cleaned_title = item['title']
        else:
            cleaned_title = "No Title"
        if 'image_extracted' in item:
            item['texts'] = item['texts'] + item['image_extracted']
        if item['texts'] == '':
            item['texts'] = 'No text'
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
    #print(f"Original text length: {len(text)} characters")  # Debug: Print original length
    
    parts = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    
    # Debug check splitting of document works
    #for i, part in enumerate(parts):
    #    print(f"Chunk {i+1} length: {len(part)} characters")  # Debug: Print chunk length
    
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


cleaned_training_data = process_data(documents)
training_data = generate_embeddings(cleaned_training_data)


# Function to escape special characters from passages to be provided as context
def clean_text(passage):
    return passage.replace("'", "").replace('"', "").replace("\n", " ")

# Function to find the best passage based on embeddings
def find_best_passage(query, training_data, top_n):
    query_embedding = genai.embed_content(model='models/text-embedding-004',
                                          content=query,
                                          task_type="retrieval_query")['embedding']
    
    scored_passages = []

    # Iterate through each document's embeddings
    for item in training_data:
        embeddings = item['embedding']  # This can be a single embedding or a list of embeddings

        # If the document has multiple embeddings (from splitting)
        if len(embeddings) > 1:
            # Compute the dot product for each chunk and store the score and text
            for embedding in embeddings:
                score = np.dot(embedding, query_embedding).sum()
                scored_passages.append((score, item['texts']))
        else:
            # If it's a single embedding
            score = np.dot(embeddings, query_embedding).sum()
            scored_passages.append((score, item['texts']))

    # Sort passages by score in descending order and return the top_n passages
    top_passages = sorted(scored_passages, key=lambda x: x[0], reverse=True)[:top_n]

    # Extract the text for the top passages
    top_texts = [clean_text(passage[1]) for passage in top_passages]

    return top_texts

# Function to create prompt based on query and relevant passage
def make_prompt(query, relevant_passages, convo_history):
    passages_text = "\n\n".join([f"PASSAGE {i+1}: '{passage}'" for i, passage in enumerate(relevant_passages)])

    prompt = textwrap.dedent(f"""\
    You are a helpful and informative customer representative that answers questions using text from the three reference passages included below. \
    You may also need to refer to contextual clues from the conversation history provided when crafting your answer. \
    Do note that you are talking to a non-technical audience, so be sure to break down complicated concepts and \
    strike a friendly and conversational tone. Please be comprehensive and include all relevant background information.    
    Be sure to respond in complete sentences and break them into succinct paragraphs and bulletpoints for readability where appropriate.\
    If the passages and previous conversation history are irrelevant to the answer, you may ignore it. \
                             
    PREVIOUS CONVERSATION: '{convo_history}'                         
    QUESTION: '{query}'
    {passages_text}

    ANSWER:
    """)
    
    # Debug - print the prompt to see formatting
    #print(prompt)
    return prompt

def send_message(request):
    if request.method == 'POST':
        genai.configure(api_key=GENERATIVE_AI_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Handle conversation_id with or without a session
        if hasattr(request, 'session') and request.session.get('conversation_id', None):
            conversation_id = request.session.get('conversation_id')
        else:
            # If no session, use conversation_id from POST data or generate a new one
            conversation_id = request.POST.get('conversation_id', None)
            if not conversation_id:
                last_message = ChatMessage.objects.aggregate(Max('id'))
                if last_message['id__max'] is None:
                    # No existing messages, start with conversation_id = 1
                    conversation_id = 1
                else:
                    # Increment from the latest id
                    conversation_id = last_message['id__max'] + 1

            # If session is available, store the conversation_id in the session
            if hasattr(request, 'session'):
                request.session['conversation_id'] = conversation_id

        user_message = request.POST.get('user_message')

        # Retrieve previous prompts and responses (limit to last 5 for brevity)
        convo_history = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('-id')[:5]
        
         # Find the 3 most relevant passages based on embeddings
        relevant_passages = find_best_passage(user_message, training_data, 3)

        # Create the prompt using the relevant passage
        prompt = make_prompt(user_message, relevant_passages, convo_history)

        bot_response = model.generate_content(prompt)
        formatted_response = markdown.markdown(bot_response.text)

        ChatMessage.objects.create(
            conversation_id=conversation_id,
            user_message=user_message, 
            bot_response=formatted_response
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

def remove_special_chars(text):
    """Remove newlines and unicode characters, and clean special characters."""
    text = text.replace('\n', ' ')  # Replace newlines with spaces
    text = text.replace('\u2019', "'")  # Replace unicode apostrophe with normal apostrophe
    return text

def remove_html_tags(text):
    """Remove HTML tags using a regular expression."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def calculate_flesch_kincaid(text):
    """Calculate the Flesch-Kincaid readability score of the provided text."""
    return textstat.flesch_reading_ease(text)

def automated_testing():
    """
    Function to run tests automatically when the server starts.
    It reuses the existing send_message function and simulates user input.
    """
    # Number of replicates per prompt
    num_replicates = 5

    # Loop to simulate conversations for testing
    for i, prompts in enumerate(tests):
        test_case_replicate_responses = []  # To accumulate all bot responses for each test case across replicates
        test_case_log = []  # Store the conversation log for each test case

        flesch_kincaid_scores = []  # Store Flesch-Kincaid scores for each replicate
    
        for replicate in range(num_replicates):
            print(f"Starting Test Case {i + 1}, Replicate {replicate + 1}...")
            conversation_id = i + 1  # Set conversation_id to i + 1 for simplicity first
            replicate_text = ""

            for prompt in prompts:
                # Simulate an HTTP POST request to send the prompt
                request = HttpRequest()
                request.method = 'POST'
                request.POST = {'user_message': prompt, 'conversation_id': conversation_id}

                # Call the existing send_message function
                send_message(request)

                # Retrieve the latest message from the database (since send_message stores it)
                last_message = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('-id').first()

                # Ensure the message was retrieved and add it to the log
                if last_message:
                    # Remove HTML tags from the bot response
                    clean_bot_response = remove_special_chars(remove_html_tags(last_message.bot_response))

                    replicate_text += " " + clean_bot_response

                    # Also accumulate responses for the whole test case (across replicates)
                    test_case_replicate_responses.append(clean_bot_response)

                    test_case_log.append({
                        "test_case": i + 1,
                        "replicate": replicate + 1,
                        "user": last_message.user_message,
                        "bot": clean_bot_response
                    })

                    # Print to debug and log progress
                    #print(f"User: {last_message.user_message}")
                    #print(f"Bot: {clean_bot_response}")
                    #print("-" * 20)

                # Simulate delay between prompts so that we don't get blocked for spamming
                time.sleep(1)
        
            # Calculate Flesch-Kincaid score for this replicate
            flesch_score = calculate_flesch_kincaid(replicate_text)
            flesch_kincaid_scores.append(flesch_score)

        # Calculate Flesch-Kincaid stats for this test case
        flesch_mean = mean(flesch_kincaid_scores)
        flesch_median = median(flesch_kincaid_scores)
        flesch_min = min(flesch_kincaid_scores)
        flesch_max = max(flesch_kincaid_scores)

        # Append the Flesch-Kincaid stats to the log for this test case
        final_stats = {
            "Flesch-Kincaid Scores": flesch_kincaid_scores,
            "Flesch-Kincaid Mean": flesch_mean,
            "Flesch-Kincaid Median": flesch_median,
            "Flesch-Kincaid Min": flesch_min,
            "Flesch-Kincaid Max": flesch_max
        }

        test_case_log.append(final_stats)

        # Save each test case's conversation log and Flesch-Kincaid stats to a separate file
        test_case_filename = f'test_case_{i + 1}.json'
        with open(test_case_filename, 'w') as f:
            json.dump(test_case_log, f, indent=4)
        print(f"Test Case {i + 1} saved in {test_case_filename}")

def runserver_test_trigger(sender, **kwargs):
    """
    This function will run automatically when the server starts using Django signals.
    """
    print("Running automated tests after server startup...")
    automated_testing()

# Django signal to trigger the tests on server startup
#request_finished.connect(runserver_test_trigger)