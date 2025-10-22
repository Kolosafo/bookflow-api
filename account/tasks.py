from .models import OTPService
def clear_otps():
    get_all_otps = OTPService.objects.all()
    for otp in get_all_otps:
        otp.delete()
        
    return "OKAY"