from .models import UserSubscriptionUsage
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def getSubcriptionUsage(summaries, notes, reminders, smart_search):
    return {
      "summaries": summaries,
      "notes": notes,
      "reminders": reminders,
      "smart_search": smart_search
      }
      


def allowedUsage(plan):
  subscription_plans = {
    "free":{
      "summaries": 1,
      "notes": 3,
      "reminders": 2,
      "smart_search": 3
      },
    "basic":{
       "summaries": 5,
      "notes": 15,
      "reminders": 5,
      "smart_search": 10
      },
    "premium":{
       "summaries": 15,
      "notes": 30,
      "reminders": 10,
      "smart_search": 25
      },
    "scholar":{
      "summaries": 50,
      "notes": 150,
      "reminders": 150,
      "smart_search": 70
    }
  }
  
  return subscription_plans[plan]

def create_subscription(user):
    UserSubscriptionUsage.objects.create(user=user)
    return True



def update_subscription_usage(user, usage):
    get_user_subscription = UserSubscriptionUsage.objects.get(user=user)
    if usage == "summaries":
        get_user_subscription.summaries -= 1
    elif usage == "notes":
        get_user_subscription.notes -= 1
    elif usage == "reminders":
        get_user_subscription.reminders -= 1
    elif usage == "smart_search":
        get_user_subscription.smart_search -= 1
    else:
        return False
    get_user_subscription.save()
    return True




def subscription_limit_required(usage_type: str):
    """
    Decorator to restrict access based on user's subscription usage.
    usage_type: 'summaries', 'notes', 'reminders', 'smart_search'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                return Response({
                    "errors": "Unauthorized",
                    "message": "Authentication required.",
                    "status": "error",
                }, status=status.HTTP_401_UNAUTHORIZED)

            try:
                subscription = UserSubscriptionUsage.objects.get(user=user)
            except UserSubscriptionUsage.DoesNotExist:
                # print("USER CANT USE THIS CUS OF SUB")
                return Response({
                    "errors": "NoSubscription",
                    "message": "No active subscription found.",
                    "status": "error",
                }, status=status.HTTP_403_FORBIDDEN)

            # Check available quota
            allowed = False
            if usage_type == "summaries" and subscription.summaries > 0:
                allowed = True
            elif usage_type == "notes" and subscription.notes > 0:
                allowed = True
            elif usage_type == "reminders" and subscription.reminders > 0:
                allowed = True
            elif usage_type == "smart_search" and subscription.smart_search > 0:
                allowed = True

            if not allowed:
                return Response({
                    "errors": "UsageLimitReached",
                    "message": f"You've reached your {usage_type} usage limit. Upgrade your plan to continue.",
                    "status": "error",
                }, status=status.HTTP_403_FORBIDDEN)

            # Continue with original view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

