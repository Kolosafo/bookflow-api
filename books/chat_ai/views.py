from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import exceptions, status
import json
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_ratelimit.decorators import ratelimit
from .main import generate_ai_chat
from ..models import ChatHistory, BookAnalysisResponse
from ..serializers import ChatHistorySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_book_ai(request):
    """
    POST view to chat with AI about a specific book
    Expected request data:
    {
        "book_id": "book_id_here",
        "book_title": "Book Title",
        "book_author": "Author Name",
        "summary": "Book summary text",
        "key_insights": "Key insights text",
        "practical_takeaways": "Practical takeaways text",
        "user_message": "User's question here"
    }
    """
    try:
        data = request.data
        book_id = data.get('book_id')
        book_title = data.get('book_title')
        book_author = data.get('book_author')
        summary = data.get('summary')
        key_insights = data.get('key_insights')
        practical_takeaways = data.get('practical_takeaways')
        user_message = data.get('user_message')

        # Validate required fields
        if not all([book_id, book_title, book_author, summary, user_message]):
            return Response({
                "errors": "book_id, book_title, book_author, summary, and user_message are required",
                "message": "Missing required fields",
                "status": "error",
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate AI response with error handling
        try:
            ai_response_json = generate_ai_chat(
                user_input=user_message,
                book_title=book_title,
                author=book_author,
                summary=summary,
                key_insights=key_insights or "",
                practical_takeaways=practical_takeaways or ""
            )
        except Exception as ai_error:
            print(f"AI Generation Error: {ai_error}")
            return Response({
                "errors": "AI generation failed",
                "message": f"Failed to generate AI response: {str(ai_error)}",
                "status": "error",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Parse the AI response
        try:
            ai_response_data = json.loads(ai_response_json)
            ai_text = ai_response_data.get('text', '')
            noteable = ai_response_data.get('noteable', '')
        except json.JSONDecodeError as json_error:
            print(f"JSON Parse Error: {json_error}")
            print(f"Raw AI Response: {ai_response_json}")
            return Response({
                "errors": "Invalid AI response format",
                "message": "Failed to parse AI response",
                "status": "error",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save chat history
        try:
            chat_history = ChatHistory.objects.create(
                user=request.user,
                book_id=book_id,
                book_title=book_title,
                book_author=book_author,
                user_message=user_message,
                ai_response=ai_text,
                noteable=noteable
            )
        except Exception as db_error:
            print(f"Database Error: {db_error}")
            # Still return the AI response even if saving fails
            return Response({
                "data": {
                    "user_message": user_message,
                    "ai_response": ai_text,
                    "noteable": noteable,
                    "book_id": book_id,
                    "book_title": book_title,
                    "book_author": book_author
                },
                "errors": "Failed to save chat history",
                "message": "Chat response generated but not saved",
                "status": "partial_success",
            }, status=status.HTTP_200_OK)

        # Serialize and return
        serializer = ChatHistorySerializer(chat_history)

        return Response({
            "data": serializer.data,
            "errors": "",
            "message": "Chat response generated successfully",
            "status": "success",
        }, status=status.HTTP_200_OK)

    except Exception as E:
        print(f"Unexpected Error: {E}")
        import traceback
        traceback.print_exc()
        return Response({
            "errors": str(E),
            "message": f"An error occurred: {E}",
            "status": "error",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, book_id):
    """
    GET view to retrieve all chat history for a specific user and book
    URL: /chat-history/<book_id>/
    """
    try:
        # Get all chat history for the user and book, ordered by creation date (newest first)
        chat_history = ChatHistory.objects.filter(
            user=request.user,
            book_id=book_id
        ).order_by('-created_at')

        if not chat_history.exists():
            return Response({
                "data": [],
                "errors": "",
                "message": "No chat history found for this book",
                "status": "success",
            }, status=status.HTTP_200_OK)

        # Serialize the data
        serializer = ChatHistorySerializer(chat_history, many=True)

        return Response({
            "data": serializer.data,
            "errors": "",
            "message": "Chat history retrieved successfully",
            "status": "success",
        }, status=status.HTTP_200_OK)

    except Exception as E:
        return Response({
            "errors": str(E),
            "message": f"An error occurred: {E}",
            "status": "error",
        }, status=status.HTTP_400_BAD_REQUEST)