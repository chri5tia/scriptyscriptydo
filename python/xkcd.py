import random
from datetime import datetime

# Sample adjectives and nouns – you can expand this
adjectives = [
    "quick", "bright", "shiny", "silent", "brave", "lazy", "happy", "curious"
]
nouns = [
    "fox", "river", "stone", "sky", "mountain", "cat", "book", "cloud"
]

def random_word():
    # 50/50 chance of adjective or noun
    return random.choice(adjectives + nouns)

def generate_phrase_password():
    words = [random_word() for _ in range(4)]
    today = datetime.now()
    suffix = f"#{today.strftime('%m%d')}"
    return " ".join(words) + " " + suffix

# Example usage
print("Generated password:", generate_phrase_password())

