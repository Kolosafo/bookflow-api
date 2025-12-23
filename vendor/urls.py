from django.urls import path
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'vendor'
urlpatterns = [
    # Book insight generation endpoint (existing)
    path('insights/<str:vendor_id>/<str:title>/<str:author>/',
         views.get_book_insight, name="get_insight"),
    path('insights/<str:vendor_id>/<str:title>/',
         views.get_book_insight, name="get_insight"),

    # Book ROI (Return on Investment) endpoint
    path('book-rio/<str:vendor_id>/', views.get_book_rio, name='get_book_rio'),

    # Vendor CRUD endpoints
    path('', views.vendor_list, name='vendor_list'),
    path('single/<str:vendor_id>/', views.vendor_detail, name='vendor_detail'),

    # BookInsight CRUD endpoints
    path('book-insights/', views.book_insight_list, name='book_insight_list'),
    path('book-insights/<int:insight_id>/', views.book_insight_detail, name='book_insight_detail'),

    # Vendor Authentication endpoints
    path('auth/signup/', views.vendor_signup, name='vendor_signup'),
    path('auth/verify-email/', views.vendor_verify_email, name='vendor_verify_email'),
    path('auth/signin/', views.vendor_signin, name='vendor_signin'),
    path('auth/resend-otp/', views.vendor_resend_otp, name='vendor_resend_otp'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
