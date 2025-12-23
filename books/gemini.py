from .AI_MODELS import GEMINI_CLIENT
from .keypoints_prompt import keypoints_prompt, main_prompt
from .book_seach_prompt import search_main_prompt, book_search_prompt
from .summary_response_format import BookAnalysisResponse
from .book_search_response_format import BookSearchResponseFormat
from .vendor_book_insights_prompt import BOOK_INSIGHTS_PROMPT, book_insight_prompt, BookInsights
from vendor.book_rio_prompt import BOOK_ROI_PROMPT, book_rio_action_prompt
from .book_rio_response_format import BookROIResponseFormat


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






# AI SEARCH
def add_summary_keyinsights_content(book_title, author=None):
    prompt = BOOK_INSIGHTS_PROMPT.format(
        book_title=book_title,
        author=author or "Unknown"
    )
    converstaion = [
        {
            "role": "model",
            "parts": [
                {"text": f"{prompt}"}
            ]
        },
        {
            "role": "user",
            "parts": [
                {"text": book_insight_prompt(book_title, author)}
            ]
        }
    ]
    
    return converstaion

def generate_book_insight(book_title, author):
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=add_summary_keyinsights_content(book_title, author),
        config={
        "response_mime_type": "application/json",
        "response_schema": BookInsights,
    },
    )

    return response.text





# Book ROI (Return on Investment) Analysis
def add_book_rio_input(book_title, reader_goal, reader_challenge, available_time, author=None):
    prompt = BOOK_ROI_PROMPT.format(
        book_title=book_title,
        author=author or "Unknown",
        reader_goal=reader_goal,
        reader_challenge=reader_challenge,
        available_time=available_time,
    )
    converstaion = [
        {
            "role": "model",
            "parts": [
                {"text": f"{prompt}"}
            ]
        },
        {
            "role": "user",
            "parts": [
                {"text": book_rio_action_prompt(book_title, author)}
            ]
        }
    ]

    return converstaion


def generate_book_rio(book_title, reader_goal, reader_challenge, available_time, author=None):
    """
    Generate Book ROI (Return on Investment) analysis
    """
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=add_book_rio_input(book_title, reader_goal, reader_challenge, available_time, author),
        config={
            "response_mime_type": "application/json",
            "response_schema": BookROIResponseFormat,
        },
    )

    return response.text
