import os
import django
import json
from rest_framework.test import APIRequestFactory
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookflow_api.settings')
django.setup()

from vendor.models import WidgetTestUsage, VendorTestKey
from vendor.views import test_book_value

def test_unique_keys():
    factory = APIRequestFactory()
    url = '/vendor/test-book-value/'
    
    # Create a test key
    test_key_str = "TEST_UNIQUE_KEY_123"
    test_key_obj, _ = VendorTestKey.objects.get_or_create(key=test_key_str)
    test_key_obj.usage_count = 0
    test_key_obj.save()
    
    data = {
        "api_key": test_key_str,
        "book_title": "Atomic Habits",
        "author": "James Clear",
        "reader_goal": "Build better habits",
        "reader_challenge": "Inconsistency",
        "available_time": "30 mins/day"
    }

    print("--- Test 1: Successful Analysis (Key Usage 1/5) ---")
    request = factory.post(url, data, format='json')
    response = test_book_value(request)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Key usage remaining: {response.data.get('key_usage_remaining')}")
        test_key_obj.refresh_from_db()
        print(f"DB Key usage count: {test_key_obj.usage_count}")

    print("\n--- Test 2: Key Limit (Simulated usage 5/5) ---")
    test_key_obj.usage_count = 5
    test_key_obj.save()
    request = factory.post(url, data, format='json')
    response = test_book_value(request)
    print(f"Status: {response.status_code} (Expected 403)")
    if response.status_code == 403:
        print("Key Limit Check: SUCCESS")

    print("\n--- Test 3: Global Limit (Simulated 120/120) ---")
    test_key_obj.usage_count = 0
    test_key_obj.save()
    today = timezone.now().date()
    usage, _ = WidgetTestUsage.objects.get_or_create(date=today)
    original_tally = usage.total_count
    usage.total_count = 120
    usage.save()
    
    request = factory.post(url, data, format='json')
    response = test_book_value(request)
    print(f"Status: {response.status_code} (Expected 429)")
    if response.status_code == 429:
        print("Global Limit Check: SUCCESS")
    
    # Restore tally
    usage.total_count = original_tally
    usage.save()
    # Clean up test key
    # test_key_obj.delete()

if __name__ == "__main__":
    test_unique_keys()
