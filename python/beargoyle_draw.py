import os
import random
import subprocess
from PIL import Image, ImageDraw

# ========== Settings ==========
CANVAS_WIDTH, CANVAS_HEIGHT = 800, 1000

# Descriptive words for filename (feel free to add more!)
DESCRIPTIVE_NAMES = [
    "snuggly", "fangly", "winged", "stitched", "grumpy", "cozy", 
    "bouncy", "batty", "punky", "gothy", "mischievous", "owlie"
]

# ========== Core Drawing Function ==========
def draw_beargoyle(draw):
    # Random ear type: round or pointy
    ear_type = random.choice(["round", "pointy"])

    # Head
    draw.ellipse((250, 150, 550, 450), outline="black", width=8)

    # Ears
    if ear_type == "round":
        draw.ellipse((220, 180, 280, 240), outline="black", width=8)
        draw.ellipse((520, 180, 580, 240), outline="black", width=8)
    else:
        draw.polygon([(250, 180), (220, 130), (280, 180)], outline="black", width=8)
        draw.polygon([(550, 180), (520, 130), (580, 180)], outline="black", width=8)

    # Button Eyes
    for x in [310, 450]:
        draw.ellipse((x, 260, x+40, 300), outline="black", width=8)
        draw.line((x+10, 270, x+30, 290), fill="black", width=5)
        draw.line((x+30, 270, x+10, 290), fill="black", width=5)

    # Body
    draw.ellipse((300, 450, 500, 700), outline="black", width=8)

    # Arms and Legs
    draw.ellipse((230, 480, 300, 600), outline="black", width=8)
    draw.ellipse((500, 480, 570, 600), outline="black", width=8)
    draw.ellipse((300, 680, 370, 780), outline="black", width=8)
    draw.ellipse((430, 680, 500, 780), outline="black", width=8)

    # Tail (random position)
    if random.random() > 0.5:
        draw.arc((350, 720, 470, 850), start=180, end=360, fill="black", width=8)
    else:
        draw.arc((300, 750, 420, 870), start=90, end=270, fill="black", width=8)

    # Wings (random style)
    wing_style = random.choice(["bat", "feather"])

    if wing_style == "bat":
        draw.polygon([(270, 500), (180, 580), (250, 600)], outline="black", width=8)
        draw.polygon([(530, 500), (620, 580), (550, 600)], outline="black", width=8)
    else:
        draw.line((270, 500, 180, 600), fill="black", width=8)
        draw.line((530, 500, 620, 600), fill="black", width=8)

    # Cape or tattoo heart
    if random.random() > 0.5:
        draw.polygon([(300, 460), (400, 400), (500, 460)], outline="black", width=8)
    else:
        draw.ellipse((375, 600, 425, 650), outline="black", width=5)  # Heart tattoo

    # Optional fangs
    if random.random() > 0.3:
        draw.polygon([(370, 400), (390, 430), (410, 400)], outline="black", width=5)
        draw.polygon([(390, 400), (410, 430), (430, 400)], outline="black", width=5)

# ========== File Naming & Saving ==========
def generate_filename():
    word = random.choice(DESCRIPTIVE_NAMES)
    return f"python_beargoyle_{word}.png"

def get_save_path(filename):
    downloads = os.path.expanduser("~/Downloads")
    return os.path.join(downloads, filename)

# ========== Main ==========
def main():
    # Create canvas
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    # Draw random Beargoyle
    draw_beargoyle(draw)

    # Save
    filename = generate_filename()
    full_path = get_save_path(filename)
    image.save(full_path)
    print(f"✅ Beargoyle saved to: {full_path}")

    # Open image (macOS only)
    try:
        subprocess.run(["open", full_path])
    except Exception:
        print("❌ Could not auto-open the image.")

if __name__ == "__main__":
    main()

