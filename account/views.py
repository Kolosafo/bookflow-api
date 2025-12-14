from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import SignUpSerializer, SupportSerializer, BioAuthSerializer, PrivacyPolicySerializer, TermsOfUsSerializer, SubscriptionUsageSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from books.tasks import SCHEDULE_FREE_TIER
from .models import OTPService, DeleteAccount, PrivacyPolicy, TermsOfUse, UserSubscriptionUsage, SubscribeInApp
from .emailFunc import send_verification_email, send_free_trial_email
from .utils import generate_otp
from books.tasks import single_free_trial
from .actions import save_otp, validate_otp
from django.core.mail import send_mail
from django.conf import settings
from .subscription_utils import getSubcriptionUsage, create_subscription, allowedUsage
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
            create_subscription(user)
            OTP = generate_otp()
            save_otp(data["email"], str(OTP), "email_verification")
            send_verification_email(data["email"], str(OTP))
            
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
        single_free_trial(check_user)
        

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
        'status',
        'subscription',
        'free_trail',
        'date_subscription_ends',
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
    
    get_previous = OTPService.objects.filter(email=email).last()
    if get_previous:
        get_previous.delete()
        
    OTP = generate_otp()
    save_otp(email, str(OTP), "email_verification")
    send_verification_email(email, str(OTP))
    
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

        send_mail("Change Password", email_message, settings.EMAIL_HOST_USER, [
            email], fail_silently=False)
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
    
    
@api_view(['POST'])
def biometric_login(request):
    data= request.data
    try:
        user = User.objects.get(email = data['email'])
        if(user.status == "blocked"):
            raise Exception("account blocked")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        serializer = BioAuthSerializer(user)
        return Response({
                "refresh": str(refresh), 
                "access": access_token,
                "data": serializer.data,
                "errors": None,
                "message": "success",
                "status": status.HTTP_200_OK,
                }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                "data": [],
                "errors": str(e),
                "message": "not found",
                "status": status.HTTP_404_NOT_FOUND,
                }, status=status.HTTP_404_NOT_FOUND)
        



@ratelimit(key='ip', rate='10/60m')
# @cache_page(60 * 60)
@api_view(["GET"])
def load_pricing(request):
    pricing_path = os.path.join(BASE_DIR, 'static', "pricing.json")
    load_pricing = open(pricing_path, 'r')
    pricing = json.load(load_pricing)
    return Response({   
        "data": pricing, 
        "message":"success",
        "status": status.HTTP_200_OK,
        }, status=status.HTTP_200_OK)
    
    

@ratelimit(key='ip', rate='1000/1d')
# @cache_page(60 * 60)
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def load_subscription_usage(request):
    user = request.user
    get_user_obj = User.objects.get(id=user.id)
    subscription_usage = UserSubscriptionUsage.objects.get(user=user)
    usage = getSubcriptionUsage(subscription_usage.summaries, subscription_usage.notes, subscription_usage.reminders, subscription_usage.smart_search)
    _allowedUsage = allowedUsage(get_user_obj.subscription)
    return Response({   
        "data": {"allowedUsage": _allowedUsage, "currentUsage":usage}, 
        "message":"success",
        "status": status.HTTP_200_OK,
        }, status=status.HTTP_200_OK)
    
    


@ratelimit(key='ip', rate='10/60m')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscribe(request):
    try:
        user = request.user
        data = request.data
        get_user = User.objects.get(id=user.id)
        SubscribeInApp.objects.create(user=get_user, productId=data['productId'], status=data['status'], amount=data['amount'], transactionRef=data['transactionRef'], data=data['data'])
        get_user.subscription=data['type']
        get_user.date_subscribed= timezone.now()
        get_user.date_subscription_ends = timezone.now().date() + timezone.timedelta(days=30)
            
        get_user.save()
        
        return Response({   
            "data": {
                     "subscription": get_user.subscription,
                     "date_subscribed":get_user.date_subscribed,
                     "date_subscription_ends": get_user.date_subscription_ends
                     }, 
            "message":"success",
            "status": status.HTTP_200_OK,
            }, status=status.HTTP_200_OK)
    except Exception as E:
        print("ERROR: ", E)
        return Response({   
            "data": None, 
            "message":"error",
            "status": status.HTTP_400_BAD_REQUEST,
            }, status=status.HTTP_400_BAD_REQUEST)
        
 
 
 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    data = request.data
    DeleteAccount.objects.create(reason=data['reason'], additionalFeedback=data['additionalFeedback'])
    user = User.objects.get(id=request.user.id)
    user.delete()
    
    return Response({   
        "data": None, 
        "message":"account successfully deleted",
        "status": status.HTTP_200_OK,
        }, status=status.HTTP_200_OK)
    


@ratelimit(key='ip', rate='10/30m')
@cache_page(60 * 60)
@api_view(['GET'])
def get_legal(request):
    try:
        policy = PrivacyPolicy.objects.filter(is_active=True).latest('created_at')
        terms = TermsOfUse.objects.filter(is_active=True).latest('created_at')
        privacy_serializer = PrivacyPolicySerializer(policy)
        terms_serializer = TermsOfUsSerializer(terms)
        return Response({
            "data": {
                "privacy": privacy_serializer.data,
                "terms": terms_serializer.data
                },
            "message": "Privacy policy retrieved successfully",
            "status": status.HTTP_200_OK
        })
    except PrivacyPolicy.DoesNotExist:
        return Response({
            "data": None,
            "message": "Privacy policy not found",
            "status": status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)
        
        

@ratelimit(key='ip', rate='10/1d')
@api_view(['POST'])
def contact_support(request):
    data = request.data
    try:
        serializer = SupportSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            
            send_mail("BookFlow Support", f"From: {data['email']} \nMessage: {data['message']}", settings.EMAIL_HOST_USER, [
            "kolosafo@gmail.com"], fail_silently=False)
            
            send_mail("BookFlow Support", f"Thanks for contacting support, your message has been recieved! \nOne of our support members will get back to you shortly. \nRegards, \BookFlow team", settings.EMAIL_HOST_USER, [
                data['email']], fail_silently=False)

            return Response({
                    "data": None,
                    "errors": False,
                    "message": "success",
                    "status": status.HTTP_200_OK,
                    }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                "data": [],
                "errors": str(e),
                "message": "not found",
                "status": status.HTTP_400_BAD_REQUEST,
                }, status=status.HTTP_400_BAD_REQUEST)
        
        


@api_view(['POST'])
def give_free_trial(request):
    try:
        SCHEDULE_FREE_TIER()
        return Response({
        "errors": None,
        "message": "success",
        "data": None,
        "status": "success",
    }, status=status.HTTP_200_OK)
    except Exception as E:
        # print("EXCEPTION: ", E)
        return Response({
            "data": None,
            "message": "not found",
            "status": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def update_subscription_usage(request):
    """
    Endpoint to update all users' subscription usage values.
    Updates all UserSubscriptionUsage records to:
    - summaries: 10
    - notes: 25
    - reminders: 10
    - smart_search: 10

    Requires authentication (staff/admin users only recommended).
    """
    try:
        # Optional: Restrict to admin/staff users only
        # if not request.user.is_staff:
        #     return Response({
        #         "errors": "Unauthorized. Admin access required.",
        #         "message": "Permission denied",
        #         "status": status.HTTP_403_FORBIDDEN,
        #     }, status=status.HTTP_403_FORBIDDEN)

        # Import the function
        from .tasks import update_all_user_subscription_usage

        # Execute the update
        result = update_all_user_subscription_usage()

        # Return success response
        if result['status'] == 'SUCCESS':
            return Response({
                "errors": None,
                "message": "Subscription usage updated successfully",
                "data": {
                    "total_users": result['total_users'],
                    "created_count": result['created_count'],
                    "updated_count": result['updated_count'],
                    "errors_count": result['errors_count'],
                    "errors": result['errors']
                },
                "status": "success",
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "errors": result.get('error', 'Unknown error'),
                "message": "Update failed",
                "data": None,
                "status": "error",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            "data": None,
            "errors": str(e),
            "message": "Internal server error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

