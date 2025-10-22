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

app_name = 'account'
urlpatterns = [
    path('register/',
         views.register, name="register"),
    # path('bio_login/', views.biometric_login, name='bio_login'),
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
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
