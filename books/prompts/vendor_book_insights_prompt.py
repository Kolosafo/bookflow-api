
from pydantic import BaseModel, Field
from typing import Optional, List


BOOK_INSIGHTS_PROMPT = """You are an expert book analyst who extracts the most valuable and actionable insights from books.

Given the book title "{book_title}" and author "{author}" (if provided), generate:

1. **Key Insights**: The 3-5 most important concepts, ideas, or lessons from the book. These should be:
   - Substantive and meaningful (not surface-level)
   - Memorable and impactful
   - Represent the core value of the book
   - Written in clear, concise language

2. **Action Steps**: 3-5 practical, specific actions readers can take to apply the book's teachings. These should be:
   - Concrete and actionable (not vague advice)
   - Achievable by most readers
   - Directly tied to the book's main themes
   - Written as clear directives

Keep each insight and action step to 1-2 sentences maximum. Focus on what makes this book unique and valuable.

Return your response in the following JSON format:
{{
  "book_title": "string",
  "author": "string (or null if unknown)",
  "key_insights": ["insight 1", "insight 2", ...],
  "action_steps": ["step 1", "step 2", ...]
}}

Ensure:
- Minimum 3 items for each list
- Maximum 5 items for each list
- Each item is concise but meaningful
- JSON is valid and properly formatted
"""



def book_insight_prompt (book_title, author=None):
    if author:
        return f"""
            Give insights and action step for the book titled "{book_title}" by {author}.
            """
    else:
        return f"""
            Give insights and action step for the book titled "{book_title}".
            """
            


class BookInsights(BaseModel):
    """Response model for book insights and action steps"""
    
    book_title: str = Field(
        ..., 
        description="The title of the book",
        min_length=1,
        max_length=300
    )
    
    author: Optional[str] = Field(
        None,
        description="The author of the book",
        max_length=150
    )
    
    key_insights: List[str] = Field(
        ...,
        description="3-5 key insights from the book",
        min_length=3,
        max_length=5
    )
    
    action_steps: List[str] = Field(
        ...,
        description="3-5 actionable steps readers can take",
        min_length=3,
        max_length=5
    )