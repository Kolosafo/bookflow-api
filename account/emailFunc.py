from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import random

def get_random_thank_you_message():
    """
    Returns a random thank you message from a predefined list,
    tailored for a fixed savings platform.
    """
    thank_you_messages = [
    "Welcome! You've just unlocked a new way to grow — not just by reading, but by truly living what you learn.",
    "Thank you for joining! Every book you explore here can become a roadmap to real-life transformation.",
    "We're glad you're here. Together, we'll turn insights from books into daily actions that actually shape your life.",
    "Welcome aboard! This is where learning meets doing — and where every great idea finds its place in your story.",
    "You've just taken the first step toward lasting growth. Let's make the wisdom you read a part of your everyday life.",
    "Thank you for trusting us on your journey. Every reflection, every reminder brings you closer to your best self.",
    "Hooray! You're in. Let's bridge the gap between knowledge and action — one book, one habit at a time.",
    "Welcome to your growth companion. Here, every lesson you read becomes a step toward a more intentional you.",
    "We're excited to have you! Get ready to transform insights into action and ideas into meaningful change.",
    "Welcome! You're not just reading books anymore — you're living their wisdom, one day at a time."
]
    

        
    return random.choice(thank_you_messages)


def send_verification_email(_email, otp):
    subject = 'Verify your email - BookFlow'
    emailVerificationTemplate = "emailVerificationTemplate.html"

    _otp_msg = "Use the code below in the BookFlow app to confirm your email address."
   
        
        
    end_msg ="If this wasn't you, please feel free to ignore this message."

    
    html_message = render_to_string(emailVerificationTemplate, {
        'otp': otp,
        'thank_you_msg': get_random_thank_you_message(),
        'otp_msg': _otp_msg,
        'end_msg': end_msg
    })

    email = EmailMessage(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [_email]
    )
    email.content_subtype = 'html'  # Set the email content type to HTML
    email.send()
    return True




def send_welcome_email(_email, first_name, language):
    subject = 'Welcome - BookFlow'
    emailVerificationTemplate = "welcomeTemplate.html"

 
    # Render the HTML template with context
    
    html_message = render_to_string(emailVerificationTemplate, {
        'first_name': first_name,
        'thank_you_msg': get_random_thank_you_message(language),
    })

    email = EmailMessage(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [_email]
    )
    email.content_subtype = 'html'  # Set the email content type to HTML
    email.send()
    return True


def send_free_trial_email(_email):
    subject = 'Congratulations - 30 Days free trial'
    freeTrailTemplate = "freeTrailTemplate.html"

 
    # Render the HTML template with context
    
    html_message = render_to_string(freeTrailTemplate)

    email = EmailMessage(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [_email]
    )
    email.content_subtype = 'html'  # Set the email content type to HTML
    email.send()
    return True
