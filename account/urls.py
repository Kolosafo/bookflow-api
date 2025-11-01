from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.urls import path, include
# from . import paystack_webhook
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import paystack_webhook

app_name = 'account'
urlpatterns = [
    path('register/',
         views.register, name="register"),
    path('bio_login/', views.biometric_login, name='bio_login'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('confirm_email/',
         views.confirm_email, name="confirm_email"),
    path('resent_otp/',
         views.resend_OTP, name="resent_otp"),
    path('forgot_password/',
         views.forgot_password, name="forgot_password"),
    path('reset_password/',
         views.password_reset, name="reset_password"),
     path('update_user_interests/',
         views.update_user_interests, name="update_user_interests"),   
    path('new-pricing/', views.load_pricing, name='load_pricing'),
    path('subscribe/', views.subscribe, name='load_pricing'),
    path('sub_usage/', views.load_subscription_usage, name='sub_usage'),
 
 
    path('delete_account/', views.delete_account, name='delete_account'),
    path('get_legal/', views.get_legal, name='get_legal'),
    path('support/', views.contact_support, name='support'),
    path('20001029/webhook/', paystack_webhook.payment_webook, name='webhook'),
        
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
