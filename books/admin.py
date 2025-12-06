from django.contrib import admin
from .models import BookAnalysisResponse, BookmarkBook, UserExtractedBooks, Notes, ChatHistory
# Register your models here.


class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book_title', 'book_author', 'truncated_user_message', 'truncated_ai_response', 'created_at')
    list_filter = ('created_at', 'book_title', 'user')
    search_fields = ('book_title', 'book_author', 'user__email', 'user_message', 'ai_response')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Book Information', {
            'fields': ('book_id', 'book_title', 'book_author')
        }),
        ('Conversation', {
            'fields': ('user', 'user_message', 'ai_response', 'noteable')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def truncated_user_message(self, obj):
        """Display first 50 characters of user message"""
        return (obj.user_message[:50] + '...') if len(obj.user_message) > 50 else obj.user_message
    truncated_user_message.short_description = 'User Message'

    def truncated_ai_response(self, obj):
        """Display first 50 characters of AI response"""
        return (obj.ai_response[:50] + '...') if len(obj.ai_response) > 50 else obj.ai_response
    truncated_ai_response.short_description = 'AI Response'


admin.site.register(BookAnalysisResponse)
admin.site.register(BookmarkBook)
admin.site.register(UserExtractedBooks)
admin.site.register(Notes)
admin.site.register(ChatHistory, ChatHistoryAdmin)
