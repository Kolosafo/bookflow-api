from django.contrib import admin
from .models import BookAnalysisResponse, BookmarkBook, UserExtractedBooks, Notes
# Register your models here.


admin.site.register(BookAnalysisResponse)
admin.site.register(BookmarkBook)
admin.site.register(UserExtractedBooks)
admin.site.register(Notes)
