from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
from .models import Post
import os 
from django_ratelimit.decorators import ratelimit
from django.views.decorators.cache import cache_page
import json
from pathlib import Path
from .ai_post_creation import generate_blog_post

BASE_DIR = Path(__file__).resolve().parent.parent



# GET all posts, POST create new post
# @ratelimit(key='ip', rate='50/1d')
# @cache_page(60 * 60)
@api_view(["GET", "POST"])
def posts_list(request):
    if request.method == "GET":
        posts = Post.objects.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        data = request.data
        API_KEY = os.getenv("POST_API_KEY", default="")
        if API_KEY != data["API_KEY"]:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET single post, PUT update, DELETE
@ratelimit(key='ip', rate='50/1d')
# @cache_page(60 * 60)
@api_view(["GET", "PUT", "DELETE"])
def post_detail(request, pk):
    try:
        post = Post.objects.get(slug=pk)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = PostSerializer(post)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        post.delete()
        return Response({"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def generate_ai_blog_post(request):
    """
    Generate an AI blog post based on a keyword.
    
    Expected payload:
    {
        "keyword": "your topic here"
    }
    """
    keyword = request.data.get('keyword')
    
    if not keyword:
        return Response(
            {"error": "Keyword is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        # Generate the blog post
        # The output_dir is relative to where the script runs, usually base dir
        result = generate_blog_post(keyword, output_dir=os.path.join(BASE_DIR, 'media', 'generated_blogs'))
        
        return Response({
            "message": "Blog post generated successfully",
            "data": result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

