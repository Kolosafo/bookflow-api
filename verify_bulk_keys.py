import os
import django
import json
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookflow_api.settings')
django.setup()

from vendor.models import VendorTestKey
from vendor.views import manage_test_keys

User = get_user_model()

def verify_bulk_management():
    factory = APIRequestFactory()
    url = '/vendor/manage-test-keys/'
    
    # Ensure we have an admin user
    admin_user, _ = User.objects.get_or_create(
        email='admin@test.com',
        defaults={'username': 'admin', 'is_staff': True, 'is_superuser': True}
    )
    
    # 1. Setup: Create some keys
    # Key to be deleted (usage >= 5)
    VendorTestKey.objects.create(key="OLD_KEY_1", usage_count=5)
    VendorTestKey.objects.create(key="OLD_KEY_2", usage_count=6)
    # Key to keep (usage < 5)
    VendorTestKey.objects.create(key="KEEP_KEY_1", usage_count=2)
    
    initial_valid_count = VendorTestKey.objects.filter(usage_count__lt=5).count()
    print(f"Initial keys with usage < 5: {initial_valid_count}")
    
    # 2. Call the endpoint
    request = factory.post(url)
    force_authenticate(request, user=admin_user)
    response = manage_test_keys(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.data
        print(f"Message: {data.get('message')}")
        new_keys = data.get('new_keys', [])
        print(f"New keys generated: {len(new_keys)}")
        
        # 3. Verify Deletion
        expired_count = VendorTestKey.objects.filter(usage_count__gte=5).count()
        print(f"Expired keys remaining in DB (should be 0): {expired_count}")
        
        # 4. Verify Generation
        total_count = VendorTestKey.objects.count()
        print(f"Total keys in DB: {total_count}")
        
        # Expected total: (initial_valid) + 50
        expected_total = initial_valid_count + 50
        if total_count == expected_total and expired_count == 0:
            print("Verification SUCCESS.")
        else:
            print(f"Verification FAILED. Expected total {expected_total}, got {total_count}.")
    else:
        print(f"Error: {response.data}")

if __name__ == "__main__":
    verify_bulk_management()
