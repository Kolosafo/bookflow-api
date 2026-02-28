from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import exceptions, status
import json
from rest_framework.permissions import AllowAny,IsAuthenticated
from .utils import search_books, get_book_by_id, search_books_by_categroy, extract_books_items
from django_ratelimit.decorators import ratelimit
from .summary_response_example import test_response
from .models import BookAnalysisResponse, UserExtractedBooks, BookmarkBook, Notes, ExtractVideoInsights, VideoNotes
from .serializers import (
    BookAnalysisResponseSerializer, 
    BookmarkBookSerializer, 
    UserExtractedBooksSerializer, 
    NotesSerializer, 
    ExtractVideoInsightsSerializer,
    VideoNotesSerializer
)
from account.subscription_utils import update_subscription_usage, subscription_limit_required
from .tasks import SCHEDULE_BOOK_SUMMARY, handle_search_book
from django.views.decorators.cache import cache_page
import os 
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .gemini import generate_video_insights
from account.utils import generate_id
from django.conf import settings

import tempfile
# Create your views here.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@subscription_limit_required('summaries')
def summarize_book(request):
    try:
        data = request.data
        book_title = data['title']
        book_id = data["id"]
        book_author = data["author"]
        book_img = data["img"]
        
        # SEE IF USER HAS ALREADY EXTRACTED THIS BOOK
        try:
            UserExtractedBooks.objects.get_or_create(user=request.user, book_id=book_id, book_author=book_author, book_title=book_title, book_img=book_img)
        except Exception as E:
            # print("ERROR CREATING EXTRACT: ", E)
            pass
        update_subscription_usage(request.user, "summaries")
        try:
            # CHECK IF BOOK ALREADY SUMMARIZED
            get_book = BookAnalysisResponse.objects.get(book_id=book_id)
            serializer = BookAnalysisResponseSerializer(get_book)
            return Response({
                    "data": serializer.data,
                    "errors": "",
                    "message": "has book",
                    "status": "error",
                }, status=status.HTTP_200_OK)
        except:
            pass
        SCHEDULE_BOOK_SUMMARY(book_title, book_author, book_id)
        # gemini_response = generate_summary_keypoints(book_title, book_author)
        # parseResponse = json.loads(gemini_response)
        # try:
        #     save_book_analysis(test_response, book_title, book_author, book_id)
        # except Exception as E:
        #     # print("COULDNT SAVE: ", E)
        #     pass
        # print("RESPONSE: ", book)
        return Response({
                "data": None,
                "errors": "",
                "message": "success",
                "status": "error",
            }, status=status.HTTP_200_OK)
    except Exception as E:
        print("SUMMARY ERROR: ", E)
        return Response({
                "errors": "ERROR",
                "message": f"An error occurred {E}",
                "status": "error",
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summarized_book(request, id):
    try:
        get_book = BookAnalysisResponse.objects.get(book_id=id)
        serializer = BookAnalysisResponseSerializer(get_book)
        return Response({
                "data": serializer.data,
                "errors": "",
                "message": "success",
                "status": "error",
            }, status=status.HTTP_200_OK)
    except Exception as E:
        print("ERROR: ", E)
        return Response({
                "errors": "ERROR",
                "message": f"An error occurred {E}",
                "status": "error",
            }, status=status.HTTP_404_NOT_FOUND)
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_books_by_category_api(request, category):
    try:
        books = search_books_by_categroy(40,category)
        # print("RESPONSE: ", book)
        return Response({
                "data": books,
                "errors": "",
                "message": "success",
                "status": "error",
            }, status=status.HTTP_200_OK)
    except Exception as E:
        return Response({
                "errors": "ERROR",
                "message": f"An error occurred {E}",
                "status": "error",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_books_api(request):
    try:
        data = request.data
        books = search_books(data["query"])
        # print("RESPONSE: ", book)
        return Response({
                "data": books,
                "errors": "",
                "message": "success",
                "status": "error",
            }, status=status.HTTP_200_OK)
    except Exception as E:
        return Response({
                "errors": "ERROR",
                "message": f"An error occurred {E}",
                "status": "error",
            }, status=status.HTTP_400_BAD_REQUEST)
        



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_book_by_id_api(request, id):
    try:
        
        book = get_book_by_id(id)
        # print("RESPONSE: ", book)
        return Response({
                "data":book,
                "errors": "",
                "message": "success",
                "status": "error",
            }, status=status.HTTP_200_OK)
    except Exception as E:
        return Response({
                "errors": "ERROR",
                "message": f"An error occurred {E}",
                "status": "error",
            }, status=status.HTTP_400_BAD_REQUEST)
        




@ratelimit(key='ip', rate='30/1d')
@api_view(["GET"])
@permission_classes([AllowAny])
def load_book_categories(request):
    try:
        category_path = os.path.join(BASE_DIR, 'static', "categories.json")
        load_categories = open(category_path, 'r')
        categories = json.load(load_categories)
        return Response({   
            "data": categories, 
            "message":"success",
            "status": status.HTTP_201_CREATED,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading pricing: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )




@ratelimit(key='ip', rate='30/1d')
@api_view(["GET"])
@permission_classes([AllowAny])
def load_popular_books(request):
    try:
        top_books_path = os.path.join(BASE_DIR, 'static', "top_books.json")
        load_books = open(top_books_path, 'r')
        top_books = json.load(load_books)
        extract_books = extract_books_items(top_books)
        # print(extract_books)
        return Response({   
            "data": extract_books, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading pricing: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


from .get_top_50_books import get_top_50
@ratelimit(key='ip', rate='30/1d')
@api_view(["GET"])
@permission_classes([AllowAny])
def get_50_books(request):
    try:
        top_50_books = get_top_50()
        return Response({   
            "data": top_50_books, 
            "message":"success",
            "status": status.HTTP_201_CREATED,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading pricing: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@ratelimit(key='ip', rate='30/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_book_mark(request):
    try:
        data = request.data
        bookmark_book, created = BookmarkBook.objects.get_or_create(book_id=data['book_id'], book_title=data['book_title'], book_author=data['book_author'], book_img=data['book_img'], user=request.user)
        serializer = BookmarkBookSerializer(bookmark_book)
        return Response({   
            "data": serializer.data, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@ratelimit(key='ip', rate='30/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_book_mark(request):
    try:
        data = request.data
        bookmark_book = BookmarkBook.objects.get(book_id=data['book_id'], user=request.user)
        bookmark_book.delete()
        return Response({   
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@ratelimit(key='ip', rate='30/1d')
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_book_marks(request):
    try:
        bookmark_books = BookmarkBook.objects.filter(user=request.user)
        serializer = BookmarkBookSerializer(bookmark_books, many=True)
        return Response({   
            "data": serializer.data, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@ratelimit(key='ip', rate='300/1d')
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_extracted_books(request):
    try:
        fetch_books = UserExtractedBooks.objects.filter(user=request.user)
        serializer = UserExtractedBooksSerializer(fetch_books, many=True)
        return Response({   
            "data": serializer.data, 
            "message":"success",
            "status": status.HTTP_201_CREATED,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@ratelimit(key='ip', rate='300/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_user_extracted_books(request):
    data = request.data
    book_id = data['book_id']
    try:
        get_book = UserExtractedBooks.objects.filter(user=request.user, book_id=book_id)
        for book in get_book:
            book.delete()
            book.save()
        return Response({   
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@ratelimit(key='ip', rate='40/60m')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@subscription_limit_required('note')
def save_note(request):
    try:
        data = request.data
        try:
            note_type = data['note_type']
        except:
            note_type = "note"
        bookmark_book, created = Notes.objects.get_or_create(content=data['content'], title=data['title'], book_id=data['book_id'], book_title=data['book_title'], book_author=data['book_author'], note_type=note_type, user=request.user)
        serializer = BookmarkBookSerializer(bookmark_book)
        update_subscription_usage(request.user, "notes")
        return Response({   
            "data": serializer.data, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        print("ERROR MSG: ", e)
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@ratelimit(key='ip', rate='30/1d')
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notes(request):
    try:
        user_notes = Notes.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotesSerializer(user_notes, many=True)
        return Response({   
            "data": serializer.data, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error loading books: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@ratelimit(key='ip', rate='30/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_note(request):
    try:
        user_notes = Notes.objects.get(user=request.user, id=request.data['id'])
        user_notes.delete()
        return Response({   
            "data": None, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error deleting note: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )




@ratelimit(key='ip', rate='30/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@subscription_limit_required('smart_search')
def ai_search_book(request):
    try:
        data = request.data
        try:
            author = data['author']
        except:
            author = None
        search_result = handle_search_book(data['title'], author)
        update_subscription_usage(request.user, "smart_search")
        return Response({   
            "data": search_result['books'], 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {
                "message": f"Error deleting note: {str(e)}",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@ratelimit(key='ip', rate='10/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@subscription_limit_required("video_extractions")
def analyze_video_insight(request):
    """
    POST: Upload a video file (max 30s recommended) and get AI insights.
    Stores video temporarily in local temp file for Gemini processing.
    """
    try:
        if 'video' not in request.FILES:
            return Response(
                {"error": "No video file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        video_file = request.FILES['video']
        
        # Validate file size (e.g., max 15MB approx 30s of decent quality)
        if video_file.size > 15 * 1024 * 1024:
             return Response(
                {"error": "Video file too large. Please upload a shorter video (max 15MB)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle local temp file creation
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            try:
                # Write uploaded chunks to temp file
                for chunk in video_file.chunks():
                    temp_video.write(chunk)
                
                temp_video_path = temp_video.name
                # print(f"Saved video to local temp: {temp_video_path}")
                
                # Generate insights using the local file path
                insights_json = generate_video_insights(temp_video_path)
                
                # Parse JSON to ensure it's valid structure
                parsed_insights = json.loads(insights_json)
                
                # Save insights to database
                save_extracted = ExtractVideoInsights.objects.create(
                    user=request.user,
                    videoTitle=request.data['video_title'],
                    # thumbnail=request.data['thumbnail'],
                    summary=parsed_insights['summary'],
                    key_takeaways=parsed_insights['key_takeaways'],
                    reminders=parsed_insights['reminders'],
                )
                
                # update_subscription_usage(request.user, "video_extractions")
                
                return Response({
                    "data": parsed_insights,
                    "saved_item_id": save_extracted.id,
                    "message": "Video analysis successful",
                    "status": status.HTTP_200_OK
                }, status=status.HTTP_200_OK)

            except Exception as e:
                print(f"AI Error: {str(e)}")
                return Response(
                    {"error": "Failed to analyze video", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            finally:
                # Cleanup: Delete the local temp file
                if os.path.exists(temp_video.name):
                    try:
                        os.remove(temp_video.name)
                        # print(f"Deleted temp video file: {temp_video.name}")
                    except Exception as e:
                        # print(f"Error deletion temp file: {e}")
                        pass

    except Exception as e:
        # print("ERROR MDG: ", str(e))
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@subscription_limit_required("video_notes")
def save_video_note(request):
    """
    POST: Save a new video note for the user.
    """
    data = request.data.copy()
    data['user'] = request.user.id
    # data['type'] = "video"
    serializer = VideoNotesSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        # update_subscription_usage(request.user, "video_notes")
        return Response({
            "data": serializer.data,
            "message": "Video note saved successfully",
            "status": status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_notes(request):
    """
    GET: Retrieve all notes for the authenticated user.
    Can be filtered by video_id via query param.
    """
    video_id = request.query_params.get('video_id')
    if video_id:
        notes = VideoNotes.objects.filter(user=request.user, video_id=video_id)
    else:
        notes = VideoNotes.objects.filter(user=request.user)
        
    serializer = VideoNotesSerializer(notes, many=True)
    return Response({
        "data": serializer.data,
        "message": "Video notes retrieved successfully",
        "status": status.HTTP_200_OK
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_video_note(request):
    """
    POST: Delete a specific video note.
    Expects note_id in request body.
    """
    note_id = request.data.get('note_id')
    if not note_id:
        return Response({"error": "note_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        note = VideoNotes.objects.get(id=note_id, user=request.user)
        note.delete()
        return Response({
            "message": "Video note deleted successfully",
            "status": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)
    except VideoNotes.DoesNotExist:
        return Response({"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)


@ratelimit(key='ip', rate='300/1d')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_extracted_videos(request):
    """
    GET: Retrieve all extracted video insights for the authenticated user.
    """
    try:
        extracted_videos = ExtractVideoInsights.objects.filter(user=request.user).order_by('-created_at')
        serializer = ExtractVideoInsightsSerializer(extracted_videos, many=True)
        return Response({
            "data": serializer.data,
            "message": "success",
            "status": status.HTTP_200_OK,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "message": f"Error loading extracted videos: {str(e)}",
            "status": status.HTTP_400_BAD_REQUEST,
        }, status=status.HTTP_400_BAD_REQUEST)


@ratelimit(key='ip', rate='300/1d')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_extracted_video(request):
    """
    POST: Delete a specific extracted video.
    Expects video_id in request body.
    """
    try:
        video_id = request.data.get('video_id')
        if not video_id:
            return Response({
                "error": "video_id is required",
                "status": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        
        extracted_video = ExtractVideoInsights.objects.get(id=video_id, user=request.user)
        extracted_video.delete()
        return Response({
            "message": "Extracted video deleted successfully",
            "status": status.HTTP_200_OK,
        }, status=status.HTTP_200_OK)
    except ExtractVideoInsights.DoesNotExist:
        return Response({
            "error": "Extracted video not found",
            "status": status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": f"Error deleting extracted video: {str(e)}",
            "status": status.HTTP_400_BAD_REQUEST,
        }, status=status.HTTP_400_BAD_REQUEST)