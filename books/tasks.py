    
from datetime import datetime, timedelta
from .scheduler import scheduler
from .save_summary import save_book_analysis
from apscheduler.triggers.date import DateTrigger
from .gemini import generate_summary_keypoints, generate_book_search
import json



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


    
