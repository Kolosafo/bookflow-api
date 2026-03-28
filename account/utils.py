import uuid
import random

def generate_id():
  return uuid.uuid4



def generate_otp():
  return str(random.randint(1000, 9999))



def generate_social_username():
    adjectives = [
        "brave", "cool", "silent", "golden", "bright", "smart", "quick", "lazy", "happy", "wild",
        "calm", "fierce", "mighty", "noble", "bold", "swift", "rare", "fancy", "sunny", "icy"
    ]
    nouns = [
        "mujahid", "wolf", "eagle", "tiger", "lion", "hunter", "path", "flow", "book", "star",
        "ocean", "forest", "mountain", "river", "sky", "earth", "spirit", "warrior", "sage", "hero"
    ]
    
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(10, 99)
    
    return f"{adjective}{noun}{number}"
