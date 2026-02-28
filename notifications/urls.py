from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'notifications'
urlpatterns = [
    path('save_notification/',
         views.save_note_notification, name="save_notification"),
    path('save_video_notification/',
         views.save_video_note_notification, name="save_video_notification"),
    path('get_notification/<str:noteId>/',
         views.get_note_notification, name="get_notification"),
    path('get_video_notification/<str:noteId>/',
         views.get_video_note_notification, name="get_video_notification"),
    path('delete_notification/<str:noteId>/', views.delete_note_notification, name="delete_notification"),
    path('delete_video_notification/<str:noteId>/', views.delete_video_note_notification, name="delete_video_notification"),
    path('times/', views.load_notification_schedule_times, name="times"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
