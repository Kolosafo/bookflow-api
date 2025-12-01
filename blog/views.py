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

