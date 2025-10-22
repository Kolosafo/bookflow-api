from .AI_MODELS import GEMINI_CLIENT
from .keypoints_prompt import keypoints_prompt, main_prompt
from .summary_response_format import BookAnalysisResponse
def add_content(book_title, author):
    converstaion = [
        {
            "role": "model",
            "parts": [
                {"text": f"{main_prompt}"}
            ]
        },
        {
            "role": "user",
            "parts": [
                {"text": keypoints_prompt(book_title, author)}
            ]
        }
    ]
    
    return converstaion

def generate_summary_keypoints(book_title, author):
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=add_content(book_title, author),
        config={
        "response_mime_type": "application/json",
        "response_schema": BookAnalysisResponse,
    },
    )

    return response.text



