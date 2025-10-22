from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import SignUpSerializer, SupportSerializer, BioAuthSerializer, PrivacyPolicySerializer, TermsOfUsSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from .models import OTPService, DeleteAccount, PrivacyPolicy, TermsOfUse
from .emailFunc import send_verification_email, send_free_trial_email
from .utils import generate_otp
from .actions import save_otp, validate_otp
from django.core.mail import send_mail
from django.conf import settings
# from notification.models import UserNotification
import json
import os
from pathlib import Path
import time
# from .helpers import send_notiifcation
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
# from .scheduler import scheduler

BASE_DIR = Path(__file__).resolve().parent.parent
# Create your views here.



@api_view(['POST'])
def register(request):
    data = request.data
            
    if User.objects.filter(email=data['email']):
        check_email_exists = User.objects.filter(email=data['email']).first()
        if check_email_exists:
            return Response({
                "errors": "email already exists",
                "message": "email already exists",
                "status": status.HTTP_409_CONFLICT,
            }, status=status.HTTP_409_CONFLICT)
            
    if data['password'] != data['password_confirm']:
        return Response({
            "errors": "Passwords do not match",
            "message": "Passwords do not match",
            "status": status.HTTP_409_CONFLICT,
        }, status=status.HTTP_409_CONFLICT)
    try:
        data['username'] = data['email']
        serializer = SignUpSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            OTP = generate_otp()
            save_otp(data["email"], str(OTP), "email_verification")
            # send_verification_email(data["email"], str(OTP))
            
            # # TRY STORYING USER PUSH NOTIFICATION
            # try:
            #     if data['pushNotificationToken']:
            #         UserNotification.objects.create(user=user, notificationToken=data['pushNotificationToken'])
            # except Exception as E:
            #     pass
            return Response({"refresh":str(refresh), "access": access_token,"data":serializer.data, "status": status.HTTP_201_CREATED})
    except Exception as e:
        return Response({
            "errors": str(e),
            "message": "An error occurred",
            "status": "error",
        }, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({
            "errors": serializer.errors,
            "message": "An error occurred",
            "status": "error",
        }, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
def confirm_email(request):
    user_email = request.data['email']
    otp = request.data['otp']
    # print("EMAIL", user_email)

    # TODO: RUN THIS ONLY IF USER ACCOUNT STATUS IS NOT ACTIVATED
    try:
        check_user = User.objects.get(email=user_email)
        if not check_user.status == "not activated":
            return Response({
                "errors": None,
                "message": "Email Already Confirmed",
                "status": status.HTTP_200_OK,
            })

        otp_validation = validate_otp(user_email, otp, "email_verification")
        if not otp_validation:
            raise ValueError(f"Invalid OTP")
 
        check_user.status = "activated"
        check_user.save()

    except Exception as E:
        # print("ERROR", E)
        return Response("Invalid OTP or User with that email doesn't exist!", status=status.HTTP_404_NOT_FOUND)

    return Response({
                "errors": None,
                "message": "success",
                "status": status.HTTP_200_OK,
            })




   
# TODO: NEW LOGIN
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    # Define which fields to include in JWT token claims (can be different from response)
    JWT_CLAIMS_FIELDS = [
        'email',
        'deviceId',
        'id',
        'interests',
        'status',
        'subscription',
        'free_trail',
        'date_subscription_ends',
        'date_subscribed'
    ]
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)            
        if user.status == "blocked":
            raise Exception("account blocked")            
        

        # Add only specified fields to JWT token claims
        for field in cls.JWT_CLAIMS_FIELDS:
            if hasattr(user, field):
                if field == "subscription":
                    value = user.subscription  # use modified value
                else:
                    value = getattr(user, field)

                # Handle date/datetime fields
                if hasattr(value, 'isoformat'):
                    token[field] = value.isoformat()
                elif value is not None:
                    token[field] = value

        return token



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = request.data
        # try:
        #     User.objects.get(username = data['username'], deviceId=data['deviceId'])
        # except Exception as e:
        #         return Response({"detail": "invalid user ID"}, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        token_data = serializer.validated_data
        return Response(token_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def resend_OTP(request):
    email = request.data['email']
    username = request.data['username']
    
    get_previous = OTPService.objects.filter(email=email).last()
    if get_previous:
        get_previous.delete()
        
    OTP = generate_otp()
    save_otp(email, str(OTP), "email_verification")
    send_verification_email(email, username, str(OTP))
    

    return Response({
                "data": None,
                "errors": None,
                "message": "success",
                "status": status.HTTP_200_OK,
    })



@api_view(['POST'])
def forgot_password(request):
    try:
        email = request.data['email']
        otp = generate_otp()
        get_user = User.objects.get(email=email.lower())
        if(get_user.status == "suspended"):
            return Response("error", status.HTTP_400_BAD_REQUEST)
        
        try:
            # DELETE ANYONE THAT ALREADY EXISTS
            reset_password = OTPService.objects.filter(email=email.lower(), type="password_reset").first()
            reset_password.delete()
        except:
            pass
        
        print("email: ", email)
        save_otp(email, otp, "password_reset")

        email_message = f"Reset your password \nHere is your One Time Password (OTP): {otp} \n\nIF YOU DIDN'T REQUEST TO CHANGE YOUR PASSWORD, PLEASE IGNORE THIS MESSAGE AND DO NOT SHARE THIS CODE WITH ANYONE, INCLUDING US. \n\nSincerely, \BookFlow Team"

        # send_mail("Change Password", email_message, settings.EMAIL_HOST_USER, [
        #     email], fail_silently=False)
        return Response({
                "data": None,
                "errors": None,
                "message": "success",
                "status": status.HTTP_200_OK,
    })
    except Exception as E:
        return Response({
                "data": None,
                "errors": True,
                "message": str(E),
                "status": status.HTTP_400_BAD_REQUEST,
    })


@api_view(['POST'])
def password_reset(request):
    data = request.data

    if data['password'] != data['confirm_password']:
        raise exceptions.APIException({
                "data": "passwords do not match",
                "errors": True,
                "message": "passwords do not match",
                "status": status.HTTP_400_BAD_REQUEST,
            }, status=status.HTTP_400_BAD_REQUEST)

    _validate_reset_otp = validate_otp(data['email'], data['otp'], "password_reset")
    if not _validate_reset_otp:
        return Response({
                "data": "invalid OTP",
                "errors": True,
                "message": "invalid OTP",
                "status": status.HTTP_400_BAD_REQUEST,
            }, status=status.HTTP_400_BAD_REQUEST)
        
    user = User.objects.filter(email=data['email'].lower()).first()
    if not user:
        return Response({
                "data": "this user does not exist",
                "errors": True,
                "message": "this user does not exist",
                "status": status.HTTP_404_NOT_FOUND,
            }, status=status.HTTP_404_NOT_FOUND)
    try:
        user.deviceId = data['deviceId']
    except:
        pass
    
    user.set_password(data['password'])
    user.save()

    return Response({
                "data": "success",
                "errors": None,
                "message": "success",
                "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_interests(request):
    """
    Update only the user's interests field.
    Any other data passed will be completely ignored.
    
    Expected payload:
    {
        "interests": ["Entrepreneurship", "Mental Health", "Investing"]
    }
    """
    user = request.user
    
    # Extract ONLY the 'interests' field from request data
    interests_data = request.data['interests']
    
    # Validate that interests data is provided
    if interests_data is None:
        return Response(
            {"error": "The 'interests' field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate that it's a list
    if not isinstance(interests_data, list):
        return Response(
            {"error": "The 'interests' field must be a list"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update ONLY the interests field, ignore everything else
    user.interests = interests_data
    user.save(update_fields=['interests'])
    
    return Response(
        {
            "message": "Interests updated successfully",
            "interests": user.interests
        },
        status=status.HTTP_200_OK
    )