
import os
import django
from django.conf import settings
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from account.views import biometric_login
from account.models import User
from rest_framework_simplejwt.tokens import AccessToken
import datetime

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookflow_api.settings')
django.setup()

def simulate_biometric_login_with_expired_token():
    factory = APIRequestFactory()
    
    # Ensure a user exists for testing
    email = "test_bio_user@example.com"
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(username=email, email=email, password="password123")
    else:
        user = User.objects.get(email=email)

    # 1. Create a request with an expired/invalid token HEADER
    # In reality, the client sends "Authorization: Bearer <expired_token>"
    # We can simulate this by manually setting the header.
    # For this test, we can just use a dummy invalid token string which should trigger 401
    # if the view relies on default global authentication classes.
    
    request = factory.post('/account/auth/biometric-login', {'email': email}, format='json')
    
    # Manually adding the header. 
    # NOTE: APIRequestFactory doesn't process middleware/auth automatically fully like the test client,
    # but we can try to invoke the view directly. 
    # However, to test the DECORATORS, we need to ensure the view wrapping happens.
    # The 'biometric_login' imported is already wrapped by @api_view.
    
    # We will simulate the "Authorization" header.
    request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_or_expired_token_string'

    try:
        response = biometric_login(request)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
        
        if response.status_code == 401 or response.status_code == 403:
             print("FAILURE REPRODUCED: Request rejected with 401/403 due to invalid token.")
        elif response.status_code == 200:
             print("SUCCESS: Request accepted despite invalid token (Auth bypassed).")
        else:
             print("OTHER RESULT")

    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    simulate_biometric_login_with_expired_token()
