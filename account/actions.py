from typing import Literal
from .models import OTPService


OtpType = Literal["email_verification", "password_reset"]

def save_otp(email:str, otp: str, type: OtpType):
  OTPService.objects.create(email=email, otp=otp, type=type)
  return True


def validate_otp(email:str, otp:str, type: OtpType):
  try:
    get_otp = OTPService.objects.get(email=email, otp=otp, type=type)
    get_otp.delete()
    return True
  except:
    return False