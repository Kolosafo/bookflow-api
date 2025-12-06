from pydantic import BaseModel, Field

class ChatResponse(BaseModel):
    """Structured response for BookFlow AI chat interactions"""
    
    text: str = Field(
        description="The full conversational response to the user's question. This should be natural, helpful, and directly address what the user asked about the book."
    )
    
    noteable: str = Field(
        description="A concise, quotable takeaway or key insight from the response that the user can save to their notes. This should be short (1-2 sentences max), actionable or memorable, and capture the essence of the advice or concept discussed. Think of it as the 'highlight' the user would want to remember later."
    )