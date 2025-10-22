import uuid
import random

def generate_id():
  return uuid.uuid4



def generate_otp():
  return random.randint(1000, 9999)


