import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import google.generativeai as genai

# Configure the Gemini API client
genai.configure(api_key=settings.GEMINI_API_KEY)

# Safety settings, temperature, etc., can be adjusted here
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Define the generative model configuration
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # Update if you're using a different model
    generation_config=generation_config
)

@csrf_exempt
def call_gemini_api(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON request
            data = json.loads(request.body)
            user_question = data.get('question')

            if not user_question:
                return JsonResponse({'error': 'No question provided'}, status=400)

            # Send the user question to Gemini 1.5
            response = send_request_to_gemini(user_question)

            # Return the response from Gemini to the user
            return JsonResponse(response, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def send_request_to_gemini(question):
    # Use the `genai.generate_text` function to send the user question to the Gemini model
    response = model.generate_content(question)

    # Return the response text
    return {"answer" : response.text}
