from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from books .gemini import generate_book_insight
import json
# Create your views here.

from .models import Vendor, BookInsight, VendorAccount
from .serializers import (
    VendorSerializer,
    VendorDetailSerializer,
    VendorCreateSerializer,
    BookInsightSerializer,
    VendorSignUpSerializer,
    VendorSignInSerializer,
    VendorVerifyEmailSerializer,
    VendorAccountSerializer
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def vendor_detail(request, vendor_id):
    """
    GET: Retrieve a specific vendor by ID
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    serializer = VendorDetailSerializer(vendor)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
    serializer = VendorSignUpSerializer(data=request.data)

    if serializer.is_valid():
        try:
            # Create vendor account
            vendor_account = serializer.save()

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

            # Link vendor to account
            vendor_account.vendor = vendor
            vendor_account.status = "activated"
            vendor_account.save()

            # Generate JWT tokens
            refresh = RefreshToken()
            refresh['vendor_account_id'] = str(vendor_account.id)
            refresh['email'] = vendor_account.email

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

            # Generate JWT tokens
            refresh = RefreshToken()
            refresh['vendor_account_id'] = str(vendor_account.id)
            refresh['email'] = vendor_account.email

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