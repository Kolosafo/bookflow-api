from google import genai
from django.conf import settings
import logging

# Suppress verbose Google Gemini logs
# logging.getLogger('google').setLevel(logging.WARNING)
# logging.getLogger('google.genai').setLevel(logging.WARNING)
# logging.getLogger('google.generativeai').setLevel(logging.WARNING)
# logging.getLogger('google.api_core').setLevel(logging.WARNING)
# logging.getLogger('urllib3').setLevel(logging.WARNING)
# logging.getLogger('httpx').setLevel(logging.WARNING)

GEMINI_CLIENT = genai.Client(api_key=settings.GOOGLE_API_KEY)

