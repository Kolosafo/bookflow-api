import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookflow_api.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from books.views import analyze_video_insight
from django.core.files.uploadedfile import SimpleUploadedFile

def test_analyze_video_direct():
    print("--- Test: Analyze Video Direct View Call ---")
    factory = APIRequestFactory()
    
    # Create dummy video content
    dummy_video_content = os.urandom(1024 * 100) # 100KB
    video_file = SimpleUploadedFile("test_video.mp4", dummy_video_content, content_type="video/mp4")
    
    request = factory.post('/books/analyze-video/', {'video': video_file}, format='multipart')
    
    try:
        response = analyze_video_insight(request)
        print(f"Status Code: {response.status_code}")
        try:
            print("Response Data:", response.data)
        except:
            print("Response Content:", response.content)
            
    except Exception as e:
        print(f"View Execution Error: {e}")

if __name__ == "__main__":
    test_analyze_video_direct()
