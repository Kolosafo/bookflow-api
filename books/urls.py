from django.urls import path
from . import views
from .chat_ai import views as chat_views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'books'
urlpatterns = [
    path('summarize/',
         views.summarize_book, name="summarize"),
     path('get_summary/<str:id>/',
         views.get_summarized_book, name="get_summary"),
    path('search/',
         views.search_books_api, name="search"),
    path('search_category/<str:category>/',
         views.search_books_by_category_api, name="search_category"),
    path('search/<str:id>/',
         views.get_book_by_id_api, name="get_book_by_id_api"),
    path('categories/',
         views.load_book_categories, name="categories"),
    path('popular_books/',
         views.load_popular_books, name="load_popular_books"),
    path('top_50/',
         views.get_50_books, name="get_50_books"),
    
    # USER BOOK URLS
     path('get_extracted/',
         views.get_user_extracted_books, name="get_extracted"),
     path('save_bookmark/',
         views.save_book_mark, name="save_bookmark"),
     path('get_bookmarks/',
         views.get_book_marks, name="get_bookmarks"),
     
     path('save_note/',
         views.save_note, name="save_note"),
     path('remove_note/',
         views.remove_note, name="remove_note"),
     path('get_notes/',
         views.get_notes, name="get_notes"),
     
     # BOOK SEARCH
    path('ai_search_book/',
         views.ai_search_book, name="ai_search_book"),

    # CHAT AI ENDPOINTS
    path('chat/',
         chat_views.chat_with_book_ai, name="chat_with_book_ai"),
    path('chat-history/<str:book_id>/',
         chat_views.get_chat_history, name="get_chat_history"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
