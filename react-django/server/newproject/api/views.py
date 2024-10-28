from django.shortcuts import render
from rest_framework.decorators import api_view
from adrf.decorators import api_view
from django.http import JsonResponse
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice,save
from dotenv import load_dotenv, find_dotenv
import os
import base64
import json
import aiofiles
import google.generativeai as genai
from .models_mongo import ChatSession, Message
import uuid
from datetime import datetime, timezone
import math
from rest_framework.response import Response

import textwrap
import numpy as np

load_dotenv(find_dotenv())
ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

## LOAD ALL ELEVENLABS VOICE IDS HERE ONCE CHAT FUNCTION IS DONE ##

@api_view(['GET'])
def hello_world(request): 
    return JsonResponse("Hello World!",safe=False)

@api_view(['PATCH'])
def update_avatar_selected(request, user_id, avatar_name):
    try: 
        chat_session = ChatSession.objects(session_id=uuid.UUID(str(user_id))).first()
        if chat_session:
            chat_session.avatarSelected = avatar_name
            chat_session.save()
            return Response({'success':True}, status=200)
        else: 
            return Response({'error': 'No chat session exists for the user'}, status=500)
    except Exception as e:
        print(f"Error in update_avatar_selected: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)

@api_view(['PATCH'])
def update_bg_selected(request, user_id, bg_name):
    try: 
        chat_session = ChatSession.objects(session_id=uuid.UUID(str(user_id))).first()
        if chat_session:
            chat_session.backgroundSelected = bg_name
            chat_session.save()
            return Response({'success':True}, status=200)
        else: 
            return Response({'error': 'No chat session exists for the user'}, status=500)
    except Exception as e:
        print(f"Error in update_bg_selected: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)

@api_view(['GET'])
def get_avatar_selected(request, user_id):
    try:
       chat_session = ChatSession.objects(session_id=uuid.UUID(str(user_id))).first()
       if chat_session:
           avatar_selected = chat_session.avatarSelected
           return JsonResponse({ 'avatar_selected': avatar_selected }, status=200)
       else: 
            return Response({'error': 'No chat session exists for the user'}, status=500)
    except Exception as e:  
        print(f"Error in retrieve_messages: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)

@api_view(['GET'])
def get_bg_selected(request, user_id):
    try:
       chat_session = ChatSession.objects(session_id=uuid.UUID(str(user_id))).first()
       if chat_session:
           bg_selected = chat_session.backgroundSelected
           return JsonResponse({ 'bg_selected': bg_selected }, status=200)
       else: 
            return Response({'error': 'No chat session exists for the user'}, status=500)
    except Exception as e:  
        print(f"Error in get_bg_selected: {e}")
        return Response({'error': 'An error occurred on the server.'}, status=500)
    
@api_view(['GET'])
def retrieve_messages(request, user_id): 
    try:
        # Find the first ChatSession object in the DB corresponding to the given userID
        chat_session = ChatSession.objects(session_id=uuid.UUID(str(user_id))).first()
        if chat_session:
            messages = [
            {
                'id': msg.id,
                'sender': msg.sender,
                'text': msg.text,
                'timestamp': msg.timestamp.isoformat(),
                'feedback': msg.feedback,  # Include feedback
            }
            for msg in chat_session.messages
        ]
            return JsonResponse({'messages': messages})
        else:
            return Response({'error': 'No chat session exists for the user'}, status=500)
    except Exception as e:
        print(f"Error in retrieve_messages: {e}")
        return JsonResponse({'error': 'An error occurred on the server.'}, status=500)
        

@api_view(['POST'])
async def chat_output(request):
    avatar_selected = request.data.get('avatarName')
    background_selected = request.data.get('backgroundName')
    user_message = request.data.get('message')
    user_id = request.data.get('id')
    if not user_message: 
        lipsync_intro_0 = await read_json_transcript("../../client/app/audios/{}_intro_0.json".format(avatar_selected))
        lipsync_intro_1 = await read_json_transcript("../../client/app/audios/{}_intro_1.json".format(avatar_selected))
        
        response = {
            "messages": [ 
                {
                    "text": "Hi, I'm {}, your professional AI assistant. ".format(avatar_selected),
                    "audio": convert_wav_base64("../../client/app/audios/{}_intro_0.wav".format(avatar_selected)),
                    "lipsync": lipsync_intro_0,
                    "facialExpression": "smile",
                    "animation": "Bow",
                    },
                {
                    "text": "Please enter your question so that I can assist you.",
                    "audio": convert_wav_base64("../../client/app/audios/{}_intro_1.wav".format(avatar_selected)),
                    "lipsync": lipsync_intro_1,
                    "facialExpression": "default",
                    "animation": "Talking0"
                    },
                ]
            }
        return JsonResponse(response)
    else: 
        prompt=user_message
        genai.configure(api_key=GEMINI_API_KEY)
        system_instruction = """"
            You are a professional assistant.
            You will always reply with a JSON array of messages. With a maximum of 3 messages.
            Each message has a text, facialExpression, and animation property.
            Do not include any emojis in the the text field of the message.
            The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
            The different animations are: Talking0, Talking1, Talking2, Bow and Idle. 
            """
        gemini_model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest', system_instruction=system_instruction)
        response_schema = {
        "type":"ARRAY",
        "items": {
            "type":"OBJECT",
            "properties": {
                "text":{"type":"STRING"},
                "facialExpression":{"type":"STRING"},
                "animation":{"type":"STRING"}
            },
            "required":["text","facialExpression","animation"]
        }, 
        }
        # WARNING: SETTING MAX_OUTPUT_TOKENS CAN RESULT IN INCOMPLETE JSONS AT TIMES, LEADING TO JSON DECODING ERROR
        generation_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=100, response_mime_type='application/json', response_schema=response_schema)
        model_response = gemini_model.generate_content(prompt, generation_config=generation_config)
        # model_response.text outputs a string in the desired JSON format
        model_response = json.loads(model_response.text) # outputs list containing max of 3 dictionaries
        for index in range(len(model_response)):
            current_dict = model_response[index]
            message_text = current_dict["text"]
            file_name = "../../client/app/audios/message_{}.mp3".format(index)
            await generate_mp3(message_text, file_name, avatar_selected)
            await generate_lip_sync(index)
            current_dict["audio"] = convert_wav_base64(file_name)
            current_dict["lipsync"] = await read_json_transcript("../../client/app/audios/message_{}.json".format(index))
        # convert model_response (list of nested dictionaries) into JSON string 
        model_response = {"messages": model_response}
        
        # Save to model response and user response to database
        if user_id:
            # Find the first ChatSession object in the DB corresponding to the given userID
            chat_session = ChatSession.objects(session_id=uuid.UUID(str(user_id))).first()
            if not chat_session:
                chat_session = ChatSession(session_id=uuid.UUID(str(user_id)))
        else:
            print("There is no user")
            # Create a user_id 
            user_id = uuid.uuid4()
            # Create new ChatSession using the newly generated user ID
            chat_session = ChatSession(session_id=uuid.UUID(str(user_id)))
        
        # Find the number of messages so an ID can be assigned to each message
        total_messages = chat_session.messages.count()
        num_user_messages = math.floor(total_messages/2)
        # Create user message that will be saved 
        user_message_obj = Message(
        id=num_user_messages+1,
        sender='User',
        text=prompt,
        timestamp=datetime.now(timezone.utc)
        )
        chat_session.messages.append(user_message_obj)
        
        # Convert bot message to string and save it 
        stringified_bot_message = convert_json_to_string(model_response)
        bot_message_obj = Message(
            id = num_user_messages+1,
            sender='Bot',
            text = stringified_bot_message,
            timestamp=datetime.now(timezone.utc)
        )
        chat_session.messages.append(bot_message_obj)
        
        # Save the avatar selected by the user 
        chat_session.avatarSelected = avatar_selected
        # Save the background selected by the user 
        chat_session.backgroundSelected = background_selected
        chat_session.save()
        return JsonResponse(model_response)
              
def convert_json_to_string(model_response):
    return ' '.join(message['text'] for message in model_response['messages'])

async def read_json_transcript(file_path):
    try:
        async with aiofiles.open(file_path, mode='r') as f:
            contents = await f.read()
            return json.loads(contents)
    except Exception as e:
        print("Error reading the JSON transcript:", e)
        return None

def convert_wav_base64(file_path):
    return base64.b64encode(open(file_path,"rb").read()).decode('utf-8')

async def generate_mp3(input_text, file_path, avatar_name):
    client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)
    name_to_voice_id_mappings = {
    "Helen":"hmD4OXeLrQIVXXUdliAG",
    "Aisha":"pMsXgVXv3BLzUgSXRplE",
    "Niraj":"zgqefOY5FPQ3bB7OZTVR", 
    "Carter":"iP95p4xoKVk53GoZ742B" 
    }
    output_audio = client.generate(text=input_text, voice=Voice(voice_id=name_to_voice_id_mappings[avatar_name]))
    save(output_audio, file_path)

async def generate_lip_sync(message_index):
    # convert mp3 audio to wav file 
    os.system("ffmpeg -y -i ../../client/app/audios/message_{}.mp3 ../../client/app/audios/message_{}.wav".format(message_index, message_index))
    # generate json file of lip movements using rhubarb lip sync
    os.system("../../client/app/rhubarb/rhubarb -f json -o ../../client/app/audios/message_{}.json ../../client/app/audios/message_{}.wav -r phonetic".format(message_index, message_index))
    
# NEED TO CHANGE TO FETCH ALL WEB SCRAPED DATA FROM MONGODB
# training_data = generate_embeddings(cleaned_training_data)

# @api_view(['POST'])
# async def chat_output(request):
#     avatar_selected = request.data.get('avatarName')
#     user_message = request.data.get('message')
#     conversation_id = request.data.get('id')
    
    #### NEEDS TO BE CHANGED TO FETCH FROM MONGODB
    # Retrieve previous prompts and responses (limit to last 5 for brevity)
    # convo_history = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('-id')[:5]

    # if not user_message: 
    #     lipsync_intro_0 = await read_json_transcript("../../client/app/audios/{}_intro_0.json".format(avatar_selected))
    #     lipsync_intro_1 = await read_json_transcript("../../client/app/audios/{}_intro_1.json".format(avatar_selected))
        
    #     response = {
    #         "messages": [ 
    #             {
    #                 "text": "Hi, I'm {}, your professional AI assistant. ".format(avatar_selected),
    #                 "audio": convert_wav_base64("../../client/app/audios/{}_intro_0.wav".format(avatar_selected)),
    #                 "lipsync": lipsync_intro_0,
    #                 "facialExpression": "smile",
    #                 "animation": "Bow",
    #                 },
    #             {
    #                 "text": "Please enter your question so that I can assist you.",
    #                 "audio": convert_wav_base64("../../client/app/audios/{}_intro_1.wav".format(avatar_selected)),
    #                 "lipsync": lipsync_intro_1,
    #                 "facialExpression": "default",
    #                 "animation": "Talking0"
    #                 },
    #             ]
    #         }
    #     return JsonResponse(response)
    # else: 
    #     genai.configure(api_key=GEMINI_API_KEY)

        # Get the LLM's response from the user query first
        # llm = genai.GenerativeModel("gemini-1.5-pro")

        # # Find the 3 most relevant passages based on embeddings
        # relevant_passages = find_best_passage(user_message, training_data, 3)

        # Create the prompt using the relevant passage
        # llm_prompt = make_prompt(user_message, relevant_passages, convo_history)
        # avatar_text = llm.generate_content(llm_prompt)

        # # Then generate avatar tone and facial expressions given the LLM's response
        # system_instruction = """"
        #     You are a professional assitant that needs to guide an AI avatar on how to read specific parts of the given response text.
        #     Create a JSON array with up to 3 messages. Each message should include a portion of the text, facialExpression 
        #     and animation property.
        #     The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
        #     The different animations are: Talking0, Talking1, Talking2, Bow and Idle. 
        #     Do not alter any words in the text. 
        #     Use the full text given across the messages, adapting expressions and animations in each to match the intended tone or emotion of that part. 
        #     Do not use emojis in the text field. 
        #     """
        # gemini_model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest', system_instruction=system_instruction)
        # response_schema = {
        # "type":"ARRAY",
        # "items": {
        #     "type":"OBJECT",
        #     "properties": {
        #         "text":{"type":"STRING"},
        #         "facialExpression":{"type":"STRING"},
        #         "animation":{"type":"STRING"}
        #     },
        #     "required":["text","facialExpression","animation"]
        # },
        # }
        # # WARNING: SETTING MAX_OUTPUT_TOKENS CAN RESULT IN INCOMPLETE JSONS AT TIMES, LEADING TO JSON DECODING ERROR
        # generation_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=100, response_mime_type='application/json', response_schema=response_schema)
        # model_response = gemini_model.generate_content(avatar_text, generation_config=generation_config)
        # # model_response.text outputs a string in the desired JSON format
        # model_response = json.loads(model_response.text) # outputs list containing max of 3 dictionaries
        # for index in range(len(model_response)):
        #     current_dict = model_response[index]
        #     message_text = current_dict["text"]
        #     file_name = "../../client/app/audios/message_{}.mp3".format(index)
        #     await generate_mp3(message_text, file_name, avatar_selected)
        #     await generate_lip_sync(index)
        #     current_dict["audio"] = convert_wav_base64(file_name)
        #     current_dict["lipsync"] = await read_json_transcript("../../client/app/audios/message_{}.json".format(index))
        # # convert model_response (list of nested dictionaries) into JSON string 
        # model_response = {"messages": model_response}
        # return JsonResponse(model_response)
    
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