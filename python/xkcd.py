import random
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    print("⚠️ 'requests' module not found. API fetch disabled.")
    HAS_REQUESTS = False

WORDLIST_FILE = "wordlist.txt"
MIN_WORDS = 100
API_LIMIT = 50


def load_words(file_path):
    if not Path(file_path).exists():
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def save_words(file_path, words):
    existing = set(load_words(file_path))
    new_words = [w for w in words if w not in existing]
    if new_words:
        with open(file_path, 'a') as f:
            for word in new_words:
                f.write(word + "\n")

def get_api_words(pos="adj", limit=API_LIMIT):
    if not HAS_REQUESTS:
        return []

    try:
        url = f"https://api.datamuse.com/words?max={limit}&md=p"
        if pos == "adj":
            url += "&topics=appearance"
        elif pos == "noun":
            url += "&topics=objects"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return [word['word'] for word in response.json() if 'tags' in word and pos in word['tags']]
    except Exception:
        return []

def ensure_wordlist(file_path):
    words = load_words(file_path)
    if len(words) >= MIN_WORDS:
        return words

    if HAS_REQUESTS:
        print("📡 Trying to fetch more words from the API...")
        new_words = get_api_words("adj") + get_api_words("noun")
        if new_words:
            print(f"✅ Retrieved {len(new_words)} new words.")
            save_words(file_path, new_words)
            words = load_words(file_path)
        else:
            print("⚠️ API call failed. Using local words only.")
    else:
        print("⚠️ Cannot use API. Using local words only.")

    return words

def generate_password(words):
    chosen = random.sample(words, 4)
    date_suffix = "#" + datetime.now().strftime("%m%d")
    return " ".join(chosen) + " " + date_suffix

if __name__ == "__main__":
    words = ensure_wordlist(WORDLIST_FILE)
    print(f"📊 Word count: {len(words)}")  # ← Add this line
    password = generate_password(words)
    ...


# 🔧 Run
if __name__ == "__main__":
    words = ensure_wordlist(WORDLIST_FILE)
    if len(words) < 4:
        print("❌ Not enough words to generate a password.")
    else:
        print("🔐 Generated password:", generate_password(words))
