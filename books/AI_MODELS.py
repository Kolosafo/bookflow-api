from google import genai
from django.conf import settings

GEMINI_CLIENT = genai.Client(api_key=settings.GOOGLE_API_KEY)

