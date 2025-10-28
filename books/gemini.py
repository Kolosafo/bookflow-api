from .AI_MODELS import GEMINI_CLIENT
from .keypoints_prompt import keypoints_prompt, main_prompt
from .book_seach_prompt import search_main_prompt, book_search_prompt
from .summary_response_format import BookAnalysisResponse
from .book_search_response_format import BookSearchResponseFormat
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





# AI SEARCH
def add_book_search_content(book_title, author=None):
    converstaion = [
        {
            "role": "model",
            "parts": [
                {"text": f"{search_main_prompt}"}
            ]
        },
        {
            "role": "user",
            "parts": [
                {"text": book_search_prompt(book_title, author)}
            ]
        }
    ]
    
    return converstaion

def generate_book_search(book_title, author):
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=add_book_search_content(book_title, author),
        config={
        "response_mime_type": "application/json",
        "response_schema": BookSearchResponseFormat,
    },
    )

    return response.text



