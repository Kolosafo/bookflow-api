    
from datetime import datetime, timedelta
from .scheduler import scheduler
from .save_summary import save_book_analysis
from apscheduler.triggers.date import DateTrigger
from .gemini import generate_summary_keypoints, generate_book_search
import json
from account.models import User, UserSubscriptionUsage
from django.utils import timezone
from account.emailFunc import send_verification_email, send_free_trial_email
from account.helpers import send_notiifcation

def summarize_and_save(book_title, book_author, book_id):
    summary = generate_summary_keypoints(book_title, book_author)
    parseResponse = json.loads(summary)
    save_book_analysis(parseResponse, book_title, book_author, book_id)
    return True

def SCHEDULE_BOOK_SUMMARY(book_title, book_author, book_id):
    run_at = datetime.now() + timedelta(seconds=2)
    scheduler.add_job(
        summarize_and_save,
        trigger=DateTrigger(run_date=run_at),
        args=[book_title, book_author, book_id],
        id=f"book_summary_{int(run_at.timestamp())}",  # unique ID
        replace_existing=False
    )
    





def handle_search_book(book_title, book_author=None):
    search_result = generate_book_search(book_title, book_author)
    parseResponse = json.loads(search_result)
    return parseResponse


    


   
    



def handle_give_free_trial():
    get_users = User.objects.filter(subscription="free")
    # try:
    #     get_subscription_model = UserSubscriptionUsage.objects.get(user=get_users)
    #     get_subscription_model
    # except:
    #     pass
    for user in get_users:
        user.subscription = "basic"
        user.free_trail_end_date = timezone.now().date() + timezone.timedelta(days=3)
        user.save()
        send_free_trial_email(get_users.email)
        try:
            pass
            # send_notiifcation(
            #     get_users.notification_token,
            #     "Congratulations - 30 Days free trial",
            #     "Congratulations - 30 Days free trial",
            #     "",
            # )
        except:
            pass
        

def SCHEDULE_FREE_TIER():
    run_at = datetime.now() + timedelta(seconds=5)
    scheduler.add_job(
        handle_give_free_trial,
        trigger=DateTrigger(run_date=run_at),
        args=[],
        id=f"give_trial_{int(run_at.timestamp())}", 
        replace_existing=False
    )
     