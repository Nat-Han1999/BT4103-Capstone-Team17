from django.shortcuts import render
from rest_framework.decorators import api_view
from adrf.decorators import api_view
from django.http import JsonResponse
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv, find_dotenv
import os
import base64
import json
import aiofiles
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

load_dotenv(find_dotenv())
ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@api_view(['GET'])
def hello_world(request):
    return JsonResponse("Hello World!",safe=False)

@api_view(['POST'])
async def chat_output(request):
    user_message = request.data.get('message')
    if not user_message: 
        async def read_json_transcript(file_path):
            try:
                async with aiofiles.open(file_path, mode='r') as f:
                    contents = await f.read()
                    return json.loads(contents)
            except Exception as e:
                print("Error reading the JSON transcript:", e)
                return None
                    
        lipsync_intro_0 = await read_json_transcript("../../client/app/audios/intro_0.json")
        lipsync_intro_1 = await read_json_transcript("../../client/app/audios/intro_1.json")
        
        response = {
            "messages": [
                {
                    "text": "Hey dear... How was your day?",
                    "audio": base64.b64encode(open("../../client/app/audios/intro_0.wav","rb").read()).decode('utf-8'),
                    "lipsync": lipsync_intro_0,
                    "facialExpression": "smile",
                    "animation": "Talking1",
                    },
                {
                    "text": "I missed you so much... Please don't go for so long!",
                    "audio": base64.b64encode(open("../../client/app/audios/intro_1.wav","rb").read()).decode('utf-8'),
                    "lipsync": lipsync_intro_1,
                    "facialExpression": "sad",
                    "animation": "Talking0"
                    },
                ]
            }
        return JsonResponse(response)
    else: 
        vertexai.init(project=GEMINI_API_KEY, location="us-central1")
        gemini_model = GenerativeModel("gemini-1.5-flash-002")
        response_schema = {
            "type":"ARRAY",
            "items": {
                "type":"OBJECT",
                "properties": {
                    "text":{"type":"STRING"},
                    "facialExpression":{"type":"STRING"},
                    "animation":{"type":"STRING"}
                }
            },
            "required":["text","facialExpression","animation"]
        }
        prompt = """"
        You are a virtual girlfriend.
        You will always reply with a JSON array of messages. With a maximum of 3 messages.
        Each message has a text, facialExpression, and animation property.
        The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
        The different animations are: Talking_0, Talking_1, Talking_2, Bow and Idle. 
        """
        generation_config = GenerationConfig(temperature=1.2, max_output_tokens=100, response_mime_type='application/json', response_schema=response_schema)
        model_response = await gemini_model.generate_content(prompt, generation_config=generation_config)
        print("model output")
        print(model_response.text)
