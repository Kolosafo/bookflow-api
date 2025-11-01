import datetime
from django.utils import timezone
import requests

paystack_ips = ["52.31.139.75", "52.49.173.169", "52.214.14.220"]

def check_ip_address(incoming_ip):
    """Checks if the incoming IP address matches any of the Paystack IP addresses.

    Args:
        incoming_ip (str): The incoming IP address to check.

    Returns:
        bool: True if the incoming IP matches, False otherwise.
    """

    return incoming_ip in paystack_ips



def get_new_day(last_login):
    time_obj = ""
    try:
        # Parse the time string with optional microseconds
        time_obj = datetime.datetime.strptime(str(last_login), "%Y-%m-%d %H:%M:%S.%f+00:00")
    except ValueError:
        # If microseconds are missing, try parsing without them
        time_obj = datetime.datetime.strptime(str(last_login), "%Y-%m-%d %H:%M:%S+00:00")
    try:
        # Convert the time object to the local timezone
        time_obj = time_obj.astimezone(timezone.get_current_timezone())
        # Get the current date and time
        now = timezone.now()
        # Check if the current day is the next day after the given time
        return now.date() > time_obj.date()
    except Exception as e:
        # Handle invalid time string format
        return False



def send_notiifcation(to, title, subTitle, body):
    
    send_notification = requests.post("https://exp.host/--/api/v2/push/send", json = {"to": to, "title": title, "subTitle": subTitle, "body": body})
    return send_notification.json()
    