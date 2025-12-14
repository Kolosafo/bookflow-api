from django.contrib import admin
from .models import BookInsight, Vendor, VendorAccount

# Register your models here.


@admin.register(BookInsight)
class BookInsightAdmin(admin.ModelAdmin):
    list_display = ['book_title', 'author_title', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['book_title', 'author_title']
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']

    fieldsets = (
        ('Book Information', {
            'fields': ('book_title', 'author_title')
        }),
        ('AI Generated Content', {
            'fields': ('insights', 'actionable_steps')
        }),
        ('Metadata', {
            'fields': ('generated_at',)
        }),
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'plan', 'daily_usage_count', 'daily_usage_limit', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['id',  'created_at', 'last_usage_reset']
    ordering = ['-created_at']

    fieldsets = (
        ('Vendor Information', {
            'fields': ('id', 'name', 'email')
        }),
        ('API Configuration', {
            'fields': ( 'plan', 'is_active')
        }),
        ('Usage Statistics', {
            'fields': ('daily_usage_count', 'daily_usage_limit', 'last_usage_reset')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields
        return ['id', 'created_at', 'last_usage_reset']


@admin.register(VendorAccount)
class VendorAccountAdmin(admin.ModelAdmin):
    list_display = ['email', 'company_name', 'status', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['email', 'company_name', 'website_url']
    readonly_fields = ['id', 'password', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Account Information', {
            'fields': ('id', 'email', 'company_name', 'website_url')
        }),
        ('Authentication', {
            'fields': ('password', 'status', 'is_active')
        }),
        ('Vendor Link', {
            'fields': ('vendor',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
