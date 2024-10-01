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

load_dotenv(find_dotenv())
ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

## LOAD ALL ELEVENLABS VOICE IDS HERE ONCE CHAT FUNCTION IS DONE ##

@api_view(['GET'])
def hello_world(request):
    return JsonResponse("Hello World!",safe=False)

@api_view(['POST'])
async def chat_output(request):
    user_message = request.data.get('message')
    if not user_message: 
        lipsync_intro_0 = await read_json_transcript("../../client/app/audios/intro_0.json")
        lipsync_intro_1 = await read_json_transcript("../../client/app/audios/intro_1.json")
        
        response = {
            "messages": [
                {
                    "text": "Hi, I'm your professional AI assistant",
                    "audio": convert_wav_base64("../../client/app/audios/intro_0.wav"),
                    "lipsync": lipsync_intro_0,
                    "facialExpression": "smile",
                    "animation": "Bow",
                    },
                {
                    "text": "Please enter your question so that I can assist you",
                    "audio": convert_wav_base64("../../client/app/audios/intro_1.wav"),
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
        generation_config = genai.GenerationConfig(temperature=0.5, max_output_tokens=100, response_mime_type='application/json', response_schema=response_schema)
        model_response = gemini_model.generate_content(prompt, generation_config=generation_config)
        # model_response.text outputs a string in the desired JSON format
        model_response = json.loads(model_response.text) # outputs list containing max of 3 dictionaries
        for index in range(len(model_response)):
            current_dict = model_response[index]
            message_text = current_dict["text"]
            file_name = "../../client/app/audios/message_{}.mp3".format(index)
            await generate_mp3(message_text, file_name)
            await generate_lip_sync(index)
            current_dict["audio"] = convert_wav_base64(file_name)
            current_dict["lipsync"] = await read_json_transcript("../../client/app/audios/message_{}.json".format(index))
        # convert model_response (list of nested dictionaries) into JSON string 
        model_response = {"messages": model_response}
        return JsonResponse(model_response)
                    
        
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

async def generate_mp3(input_text, file_path):
    client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)
    output_audio = client.generate(text=input_text, voice=Voice(voice_id="hmD4OXeLrQIVXXUdliAG"))
    save(output_audio, file_path)

async def generate_lip_sync(message_index):
    # convert mp3 audio to wav file 
    os.system("ffmpeg -y -i ../../client/app/audios/message_{}.mp3 ../../client/app/audios/message_{}.wav".format(message_index, message_index))
    # generate json file of lip movements using rhubarb lip sync
    os.system("../../client/app/rhubarb/rhubarb -f json -o ../../client/app/audios/message_{}.json ../../client/app/audios/message_{}.wav -r phonetic".format(message_index, message_index))