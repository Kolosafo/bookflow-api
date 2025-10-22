from django.contrib import admin
from .models import User, OTPService, SubscribeInApp, DeleteAccount, PrivacyPolicy, TermsOfUse, SupportMessage, PaystackResponse
# Register your models here.
admin.site.register(OTPService)
admin.site.register(SubscribeInApp)
admin.site.register(DeleteAccount)
admin.site.register(PaystackResponse)
admin.site.register(PrivacyPolicy)
admin.site.register(TermsOfUse)
admin.site.register(SupportMessage)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'subscription', 'free_trail', 'date_joined')
    list_filter = ('email',)
    search_fields = ('email',)
    date_hierarchy = 'date_joined'
    ordering = ('-date_joined',)