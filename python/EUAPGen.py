import random
import string

def generate_password():
    while True:
        # First character: must be a letter
        first_char = random.choice(string.ascii_letters)

        # Remaining 7 characters
        remaining_chars = []

        # Ensure at least one of each required type is included
        remaining_chars.append(random.choice(string.ascii_uppercase))
        remaining_chars.append(random.choice(string.ascii_lowercase))
        remaining_chars.append(random.choice(string.digits))

        # Fill the rest (4 characters) with random choices from all sets
        all_chars = string.ascii_letters + string.digits
        while len(remaining_chars) < 7:
            remaining_chars.append(random.choice(all_chars))

        # Shuffle the remaining characters and combine with the first one
        random.shuffle(remaining_chars)
        password = first_char + ''.join(remaining_chars)

        # Double-check it meets the criteria (safety net)
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            len(password) == 8 and
            password[0].isalpha()):
            return password

# Example usage
print("Generated password:", generate_password())

