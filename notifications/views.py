from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import exceptions, status
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import IsAuthenticated
from .models import NoteNotification
from account.models import User
from books.models import Notes
from .serializers import NoteNotificationSerializer
from account.subscription_utils import update_subscription_usage, subscription_limit_required
import json
import os 
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
# Create your views here.


@ratelimit(key='ip', rate='30/1d')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@subscription_limit_required("reminders")
def save_note_notification(request):
    try:
        data = request.data
        note_notification_book, created = NoteNotification.objects.get_or_create(frequency=data['frequency'], reminder_time=data['reminderTime'], title=data['title'], noteId=data['noteId'], content=data['content'], user=request.user)
        serializer = NoteNotificationSerializer(note_notification_book)
        # handle update the note itself
        try:
            get_note = Notes.objects.get(id=data['noteId'], user=request.user)
            get_note.has_notification = True
            get_note.save()
        except:
            pass
        
        try:
            if data['notificationToken']:
                get_user = User.objects.get(id=request.user.id)
                get_user.notification_token = data['notificationToken']
                get_user.save()
            
        except Exception as e:
            pass        
        update_subscription_usage(request.user, "reminders")
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
@api_view(['POST'])
def delete_note_notification(request, noteId):
    try:
        get_note = Notes.objects.get(id=noteId)
        get_note.has_notification = False
        get_note.save()
        get_notification = NoteNotification.objects.get(noteId=noteId)
        get_notification.delete()
        return Response({
                "data": "success",
                "errors": "",
                "message": "success",
                "status": "error",
            }, status=status.HTTP_200_OK)
    except Exception as E:
        return Response({
                "errors": "ERROR",
                "message": f"An error occurred {E}",
                "status": "error",
            }, status=status.HTTP_404_NOT_FOUND)
        
        

@ratelimit(key='ip', rate='30/1d')
@api_view(['GET'])
def get_note_notification(request, noteId):
    try:
        get_notification = NoteNotification.objects.get(noteId=noteId)
        serializer = NoteNotification(get_notification)
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
        
        


@ratelimit(key='ip', rate='30/1d')
@api_view(["GET"])
def load_notification_schedule_times(request):
    try:
        notification_times = os.path.join(BASE_DIR, 'static', "notification_times.json")
        load_times = open(notification_times, 'r')
        times = json.load(load_times)
        
        # print(extract_books)
        return Response({   
            "data": times, 
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