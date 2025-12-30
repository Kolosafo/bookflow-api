from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from books.gemini import generate_book_insight, generate_book_rio
from django.core.mail import EmailMessage
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
import os

import json
from django.conf import settings
from account.utils import generate_id
from django.template.loader import render_to_string
# Create your views here.

from .models import Vendor, BookInsight, VendorAccount, BookROI, WidgetTestUsage, VendorTestKey
from account.models import User
from .serializers import (
    VendorSerializer,
    VendorDetailSerializer,
    VendorCreateSerializer,
    BookInsightSerializer,
    VendorSignUpSerializer,
    VendorSignInSerializer,
    VendorVerifyEmailSerializer,
    VendorAccountSerializer,
    BookROIRequestSerializer,
    BookROISerializer
)

# Import OTP utilities from account app
from account.utils import generate_otp
from account.actions import save_otp, validate_otp
from account.emailFunc import send_verification_email


@ratelimit(key="ip", rate="1000/1d", block=True)
@cache_page(60 * 60)  # Cache for 1 hour
@api_view(["GET"])
def get_book_insight(request, vendor_id, title, author=None):

    if not vendor_id:
        return Response(
            {"error": "Vendor ID (api_key) is required"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        vendor = Vendor.objects.get(id=vendor_id, is_active=True)
    except Vendor.DoesNotExist:
        return Response(
            {"error": "Invalid or inactive vendor"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check daily usage
    if not vendor.can_use_api():
        return Response(
            {
                "error": "Daily usage limit exceeded",
                "plan": vendor.plan,
                "daily_limit": vendor.daily_usage_limit,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Generate insight
    ai_response = generate_book_insight(title, author)
    parsed_response = json.loads(ai_response)
    
    # print("RESPONSE: ", parsed_response)
    # Increment usage
    vendor.increment_usage()

    return Response(
        {
            "insight": "insight",
            "actionable_steps": "action_steps",
            # "usage": {
            #     "used_today": vendor.daily_usage_count,
            #     "daily_limit": vendor.daily_usage_limit,
            #     "plan": vendor.plan,
            # },
        },
        status=status.HTTP_200_OK
    )


# Vendor endpoints
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def vendor_list(request):
    """
    GET: List all vendors
    POST: Create a new vendor
    """
    if request.method == 'GET':
        vendors = Vendor.objects.all().order_by('-created_at')
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = VendorCreateSerializer(data=request.data)
        if serializer.is_valid():
            vendor = serializer.save()
            # Return the created vendor with API key
            response_serializer = VendorDetailSerializer(vendor)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def vendor_detail(request, vendor_id):
    """
    GET: Retrieve a specific vendor by ID
    PATCH: Update a specific vendor by ID
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'GET':
        serializer = VendorDetailSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        # Only allow updating dropdown_preview_text
        update_data = {}
        if 'dropdown_preview_text' in request.data:
            update_data['dropdown_preview_text'] = request.data.get('dropdown_preview_text')
        
        if 'is_widget_open_by_default' in request.data:
            update_data['is_widget_open_by_default'] = request.data.get('is_widget_open_by_default')
        
        if not update_data:
            return Response(
                {"error": "Only 'dropdown_preview_text' can be updated via this endpoint"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VendorDetailSerializer(vendor, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_widget_settings(request, vendor_id):
    """
    GET: Retrieve only the dropdown_preview_text for a specific vendor
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    return Response({
        "dropdown_preview_text": vendor.dropdown_preview_text,
        "is_widget_open_by_default": vendor.is_widget_open_by_default
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def test_book_value(request):
    """
    POST: Free trial endpoint for vendors to test the widget.
    Each unique API key has a lifetime limit of 5 uses.
    Global limit is 120 analyses per day.
    """
    # Verify Vendor Test API Key
    api_key_str = request.data.get('api_key')
    if not api_key_str:
        return Response(
            {"error": "API Key is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        test_key_obj = VendorTestKey.objects.get(key=api_key_str)
    except VendorTestKey.DoesNotExist:
        return Response(
            {"error": "Invalid Test API Key"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if key can still be used (limit 5)
    if not test_key_obj.can_be_used():
        return Response(
            {"error": "This test API key has reached its maximum usage limit of 5. Please contact support for more information."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check global daily limit (limit 120)
    if WidgetTestUsage.get_count_for_today() >= 120:
        return Response(
            {"error": "Global daily limit for free tests reached. Please try again tomorrow or contact support."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Validate request data
    serializer = BookROIRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Invalid request data",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    book_title = validated_data['book_title']
    author = validated_data.get('author', None)
    reader_goal = validated_data['reader_goal']
    reader_challenge = validated_data['reader_challenge']
    available_time = validated_data['available_time']

    try:
        # Generate ROI analysis
        ai_response = generate_book_rio(
            book_title=book_title,
            reader_goal=reader_goal,
            reader_challenge=reader_challenge,
            available_time=available_time,
            author=author
        )
        parsed_response = json.loads(ai_response)

        # Increment both per-key usage and global usage tally
        test_key_obj.increment_usage()
        WidgetTestUsage.increment_count()

        return Response(
            {
                "data": parsed_response,
                "message": "Free test analysis successful",
                "key_usage_remaining": 5 - test_key_obj.usage_count,
                "global_tests_remaining_today": max(0, 120 - WidgetTestUsage.get_count_for_today())
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "error": "Failed to generate ROI analysis",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def manage_test_keys(request):
    """
    POST: Manage VendorTestKey records.
    1. Delete keys that have reached usage limit (>=5).
    2. Generate 50 new unique API keys.
    """
    
    # 2. Generate 50 new keys
    new_keys = []
    for _ in range(50):
        new_key = VendorTestKey.objects.create()
        new_keys.append(new_key.key)
    
    return Response({
        "message": f"Cleanup successful (expired keys deleted) and 50 new keys generated.",
        "new_keys": new_keys
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def generate_vendor_outreach_email(request):
    """
    POST: Generate an outreach email for a vendor using the contact-vendor.html template.
    Assigns an unassigned VendorTestKey to the vendor and marks it as assigned.
    Parameters required in request data:
    - blogger_name
    - blog_name
    """
    # required_params = ['blogger_name', 'blog_name', 'praise_hook', 'audience_focus']
    # for param in required_params:
    #     if param not in request.data:
    #         return Response(
    #             {"error": f"Missing required parameter: {param}"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    # Find an unassigned key
    test_key = VendorTestKey.objects.filter(is_assigned=False, is_active=True).first()
    
    if not test_key:
        return Response(
            {"error": "No unassigned test API keys available. Please generate more keys using /manage-test-keys/."},
            status=status.HTTP_404_NOT_FOUND
        )



    try:
        # LOADING BLOGS DATA FROM JSON
        emails_path = os.path.join(BASE_DIR, 'static', "cold_email_list.json")
        load_emails_data = open(emails_path, 'r')
        cold_email_list = json.load(load_emails_data)
        
        for email_data in cold_email_list:
            # Render context
            context = {
                'blogger_name': email_data['blogger_name'],
                'blog_name': email_data['blog_name'],
                'praise_hook': email_data['praise_hook'],
                'audience_focus': email_data['audience_focus'],
                'api_key': test_key.key
            }
            # Render the template to string
            html_content = render_to_string('contact-vendor.html', context)
            subject = f"Partnership opportunity for {email_data['blog_name']}"
    
            
            email = EmailMessage(
                subject,
                html_content,
                "Dauda Kolo",
                ["kolosafo@gmail.com"]
                )
            email.content_subtype = 'html'  # Set the email content type to HTML
            email.send()
            # Mark the key as assigned
            test_key.is_assigned = True
            test_key.save()

        return Response({
            "message": "Outreach email generated successfully",
            "api_key_assigned": test_key.key,
            # "html_content": html_content
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "Failed to render email template", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# BookInsight GET endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def book_insight_list(request):
    """
    GET: List all book insights
    Optional query parameters:
    - book_title: Filter by book title (case-insensitive search)
    - author_title: Filter by author title (case-insensitive search)
    """
    queryset = BookInsight.objects.all().order_by('-generated_at')

    # Optional filtering
    book_title = request.query_params.get('book_title', None)
    author_title = request.query_params.get('author_title', None)

    if book_title:
        queryset = queryset.filter(book_title__icontains=book_title)
    if author_title:
        queryset = queryset.filter(author_title__icontains=author_title)

    serializer = BookInsightSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def book_insight_detail(request, insight_id):
    """
    GET: Retrieve a specific book insight by ID
    """
    insight = get_object_or_404(BookInsight, id=insight_id)
    serializer = BookInsightSerializer(insight)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vendor Authentication Views

@api_view(['POST'])
def vendor_signup(request):
    """
    POST: Register a new vendor account
    Sends OTP to email for verification
    """
    data = request.data
    check_email_exists = VendorAccount.objects.filter(email=data['email']).first()
    if check_email_exists:
        return Response({
            "errors": "email already exists",
            "message": "email already exists",
            "status": status.HTTP_409_CONFLICT,
        }, status=status.HTTP_409_CONFLICT)
    
    # Also check if User with this email exists
    if User.objects.filter(email=data['email']).exists():
        return Response({
            "errors": "email already exists",
            "message": "email already exists",
            "status": status.HTTP_409_CONFLICT,
        }, status=status.HTTP_409_CONFLICT)
        
    serializer = VendorSignUpSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Create vendor account
            vendor_account = serializer.save()
            
            # Create User profile for vendor (for JWT authentication)
            user = User.objects.create_user(
                email=vendor_account.email,
                username=vendor_account.email,
                password=data['password'],  # Use raw password from request
                type="vendor",
                status="not activated",
                deviceId=str(generate_id())  # Generate unique device ID
            )
            
            # Link user to vendor account
            vendor_account.user = user
            vendor_account.save()

            # Generate and send OTP
            otp = generate_otp()
            save_otp(vendor_account.email, str(otp), "email_verification")
            send_verification_email(vendor_account.email, str(otp))

            return Response({
                "data": {
                    "email": vendor_account.email,
                    "company_name": vendor_account.company_name,
                    "status": vendor_account.status
                },
                "message": "Account created successfully. Please check your email for verification code.",
                "errors": None,
                "status": status.HTTP_201_CREATED
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "data": None,
                "message": "Failed to create account",
                "errors": str(e),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "data": None,
        "message": "Validation failed",
        "errors": serializer.errors,
        "status": status.HTTP_400_BAD_REQUEST
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def vendor_verify_email(request):
    """
    POST: Verify vendor email with OTP
    Creates Vendor instance and returns tokens upon successful verification
    """
    serializer = VendorVerifyEmailSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        otp = serializer.validated_data['otp']

        try:
            # Get vendor account
            vendor_account = VendorAccount.objects.get(email=email)

            # Check if already activated
            if vendor_account.status == "activated":
                return Response({
                    "data": None,
                    "message": "Account is already activated",
                    "errors": "Account already activated",
                    "status": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate OTP
            if not validate_otp(email, otp, "email_verification"):
                return Response({
                    "data": None,
                    "message": "Invalid or expired OTP",
                    "errors": "Invalid OTP",
                    "status": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create Vendor instance with API key
            vendor = Vendor.objects.create(
                name=vendor_account.company_name,
                email=vendor_account.email,
                plan="free",
                daily_usage_limit=1000
            )

            # Link vendor to account and activate
            vendor_account.vendor = vendor
            vendor_account.status = "activated"
            vendor_account.save()
            
            # Activate the User profile
            if vendor_account.user:
                vendor_account.user.status = "activated"
                vendor_account.user.save()

            # Generate JWT tokens using User profile
            refresh = RefreshToken.for_user(vendor_account.user)

            # Serialize account data
            account_serializer = VendorAccountSerializer(vendor_account)

            return Response({
                "data": account_serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                },
                "message": "Email verified successfully",
                "errors": None,
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        except VendorAccount.DoesNotExist:
            return Response({
                "data": None,
                "message": "Vendor account not found",
                "errors": "Account does not exist",
                "status": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "data": None,
                "message": "Verification failed",
                "errors": str(e),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "data": None,
        "message": "Validation failed",
        "errors": serializer.errors,
        "status": status.HTTP_400_BAD_REQUEST
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def vendor_signin(request):
    """
    POST: Sign in vendor account
    Returns access and refresh tokens
    """
    serializer = VendorSignInSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']

        try:
            # Get vendor account
            vendor_account = VendorAccount.objects.get(email=email)

            # Check if account is suspended
            if vendor_account.status == "suspended":
                return Response({
                    "data": None,
                    "message": "Account is suspended",
                    "errors": "Account suspended",
                    "status": status.HTTP_403_FORBIDDEN
                }, status=status.HTTP_403_FORBIDDEN)

            # Check if account is activated
            if vendor_account.status == "not activated":
                return Response({
                    "data": None,
                    "message": "Please verify your email first",
                    "errors": "Email not verified",
                    "status": status.HTTP_403_FORBIDDEN
                }, status=status.HTTP_403_FORBIDDEN)

            # Verify password
            if not vendor_account.check_password(password):
                return Response({
                    "data": None,
                    "message": "Invalid email or password",
                    "errors": "Invalid credentials",
                    "status": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Check if account is active
            if not vendor_account.is_active:
                return Response({
                    "data": None,
                    "message": "Account is inactive",
                    "errors": "Account inactive",
                    "status": status.HTTP_403_FORBIDDEN
                }, status=status.HTTP_403_FORBIDDEN)

            # Generate JWT tokens using User profile
            refresh = RefreshToken.for_user(vendor_account.user)

            # Serialize account data
            account_serializer = VendorAccountSerializer(vendor_account)

            return Response({
                "data": account_serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                },
                "message": "Login successful",
                "errors": None,
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        except VendorAccount.DoesNotExist:
            return Response({
                "data": None,
                "message": "Invalid email or password",
                "errors": "Invalid credentials",
                "status": status.HTTP_401_UNAUTHORIZED
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "data": None,
                "message": "Login failed",
                "errors": str(e),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "data": None,
        "message": "Validation failed",
        "errors": serializer.errors,
        "status": status.HTTP_400_BAD_REQUEST
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def vendor_resend_otp(request):
    """
    POST: Resend OTP to vendor email
    """
    email = request.data.get('email')

    if not email:
        return Response({
            "data": None,
            "message": "Email is required",
            "errors": "Email missing",
            "status": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        email = email.lower()
        vendor_account = VendorAccount.objects.get(email=email)

        if vendor_account.status == "activated":
            return Response({
                "data": None,
                "message": "Account is already activated",
                "errors": "Account already activated",
                "status": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate and send new OTP
        otp = generate_otp()
        save_otp(email, str(otp), "email_verification")
        send_verification_email(email, str(otp))

        return Response({
            "data": None,
            "message": "OTP sent successfully",
            "errors": None,
            "status": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

    except VendorAccount.DoesNotExist:
        return Response({
            "data": None,
            "message": "Vendor account not found",
            "errors": "Account does not exist",
            "status": status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "data": None,
            "message": "Failed to resend OTP",
            "errors": str(e),
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Book ROI endpoint
@ratelimit(key="ip", rate="120/1d", block=True)
@api_view(["POST"])
def get_book_rio(request, vendor_id):
    """
    POST: Get Book ROI (Return on Investment) analysis
    Helps readers determine if a book is worth their time based on their goals
    """
    if not vendor_id:
        return Response(
            {"error": "Vendor ID (api_key) is required"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        vendor = Vendor.objects.get(id=vendor_id, is_active=True)
    except Vendor.DoesNotExist:
        return Response(
            {"error": "Invalid or inactive vendor"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check daily usage
    if not vendor.can_use_api():
        return Response(
            {
                "error": "Daily usage limit exceeded",
                "plan": vendor.plan,
                "daily_limit": vendor.daily_usage_limit,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Validate request data
    serializer = BookROIRequestSerializer(data=request.data)
    if not serializer.is_valid():
        # print("ERROR: ", serializer.errors)
        return Response(
            {
                "error": "Invalid request data",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    book_title = validated_data['book_title']
    author = validated_data.get('author', None)
    reader_goal = validated_data['reader_goal']
    reader_challenge = validated_data['reader_challenge']
    available_time = validated_data['available_time']

    try:
        # Generate ROI analysis
        ai_response = generate_book_rio(
            book_title=book_title,
            reader_goal=reader_goal,
            reader_challenge=reader_challenge,
            available_time=available_time,
            author=author
        )
        parsed_response = json.loads(ai_response)

        # Save to database
        book_roi = BookROI.objects.create(
            book_title=book_title,
            author=author or "",
            reader_goal=reader_goal,
            reader_challenge=reader_challenge,
            available_time=available_time,
            roi_score=parsed_response['roi_score'],
            match_reasoning=parsed_response['match_reasoning'],
            relevant_takeaways=parsed_response['relevant_takeaways'],
            time_analysis=parsed_response['time_analysis'],
            estimated_reading_hours=parsed_response['estimated_reading_hours'],
            recommendation=parsed_response['recommendation']
        )

        # Increment usage
        vendor.increment_usage()

        # Serialize and return response
        response_serializer = BookROISerializer(book_roi)

        return Response(
            {
                "data": response_serializer.data,
                "usage": {
                    "used_today": vendor.daily_usage_count,
                    "daily_limit": vendor.daily_usage_limit,
                    "plan": vendor.plan,
                },
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "error": "Failed to generate ROI analysis",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




import json
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import VendorTestKey

@api_view(["GET"])
def assign_vendor_keys(request):
    emails_path = os.path.join(BASE_DIR, 'static', "cold_email_list.json")
    load_emails_data = open(emails_path, 'r')
    input_data = json.load(load_emails_data)

    updated_data = []
    num_items = len(input_data)

    with transaction.atomic():
        # 1. Fetch a batch of unique, unassigned keys using select_for_update()
        # We filter for is_assigned=False to ensure each website gets a UNIQUE key.
        available_keys = list(
            VendorTestKey.objects.select_for_update()
            .filter(is_active=True, is_assigned=False, usage_count__lt=5)
            [:num_items] # Only take as many as we have items in the JSON
        )

        # 2. Assign keys to items
        for i, item in enumerate(input_data):
            if i < len(available_keys):
                key_obj = available_keys[i]
                
                # Update JSON
                item['api_key'] = key_obj.key
                
                # Update Model
                key_obj.is_assigned = True
                key_obj.increment_usage() # This increments usage and calls .save()
            else:
                # Fallback if you run out of keys in the database
                item['api_key'] = None
            
            updated_data.append(item)

    return JsonResponse(updated_data, safe=False)


@ratelimit(key="ip", rate="1/1d", block=True)
@api_view(['GET'])
def create_assigned_test_key(request):
    """
    GET: Create a new VendorTestKey, mark it as assigned, and return the API key.
    """
    try:
        # Create a new test key
        new_key = VendorTestKey.objects.create(is_assigned=True)
        
        return Response({
            "message": "Test API key created and assigned successfully",
            "api_key": new_key.key
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            "error": "Failed to create test API key",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)