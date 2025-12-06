from ..AI_MODELS import GEMINI_CLIENT
from .chat_ai_prompt import get_bookflow_prompt
from .response_format import ChatResponse
def add_content(user_input, book_title, author, summary, key_insights, practical_takeaways):
    converstaion = [
        {
            "role": "model",
            "parts": [
                {"text": f"{get_bookflow_prompt(book_title, author, summary, key_insights, practical_takeaways)}"}
            ]
        },
        {
            "role": "user",
            "parts": [
                {"text": user_input}
            ]
        }
    ]
    return converstaion

def generate_ai_chat(user_input, book_title, author, summary, key_insights, practical_takeaways):
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=add_content(user_input, book_title, author, summary, key_insights, practical_takeaways),
        config={
        "response_mime_type": "application/json",
        "response_schema": ChatResponse,
    },
    )

    return response.text
