import os
import django
import json
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookflow_api.settings')
django.setup()

from vendor.models import VendorTestKey
from vendor.views import generate_vendor_outreach_email

User = get_user_model()

def verify_outreach_email():
    factory = APIRequestFactory()
    url = '/vendor/outreach-email/'
    
    # Ensure we have an admin user
    admin_user, _ = User.objects.get_or_create(
        email='admin@test.com',
        defaults={'username': 'admin', 'is_staff': True, 'is_superuser': True}
    )
    
    # 1. Setup: Ensure we have at least one unassigned key
    test_key_str = "OUTREACH_TEST_KEY"
    test_key, _ = VendorTestKey.objects.get_or_create(key=test_key_str)
    test_key.is_assigned = False
    test_key.save()
    
    data = {
        "blogger_name": "Jane Doe",
        "blog_name": "Jane's Book Nook",
        "widget_preview_image_url": "https://example.com/preview.png",
        "widget_signup_url": "https://getbookflow.com/signup"
    }

    print("--- Test: Generating Outreach Email ---")
    request = factory.post(url, data, format='json')
    force_authenticate(request, user=admin_user)
    response = generate_vendor_outreach_email(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        res_data = response.data
        print(f"Message: {res_data.get('message')}")
        assigned_key = res_data.get('api_key_assigned')
        print(f"Assigned Key: {assigned_key}")
        
        # Verify it's in the HTML
        html = res_data.get('html_content')
        if assigned_key in html:
            print("Key found in rendered HTML: SUCCESS")
        else:
            print("Key NOT found in rendered HTML: FAILED")
            
        # Verify key is marked as assigned in DB
        test_key.refresh_from_db()
        print(f"Key is_assigned in DB: {test_key.is_assigned}")
        if test_key.is_assigned == True:
            print("DB Update: SUCCESS")
        else:
            print("DB Update: FAILED")
            
        # Try to assign again - should get a different key or error if none available
        print("\n--- Test: Attempting to assign again (should use different key) ---")
        request2 = factory.post(url, data, format='json')
        force_authenticate(request2, user=admin_user)
        response2 = generate_vendor_outreach_email(request2)
        
        if response2.status_code == 200:
            assigned_key2 = response2.data.get('api_key_assigned')
            print(f"Second assigned Key: {assigned_key2}")
            if assigned_key2 != assigned_key:
                print("Unique assignment: SUCCESS")
            else:
                print("Assignment DUPLICATED: FAILED")
        else:
            print(f"Second attempt failed (possibly no more keys): {response2.data}")
            
    else:
        print(f"Error: {response.data}")

if __name__ == "__main__":
    verify_outreach_email()
