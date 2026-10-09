from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


PROJECT_DIR = Path(__file__).resolve().parents[2]
ASSETS = PROJECT_DIR / "assets"
OUTPUT = PROJECT_DIR / "ai_test_images"
OUTPUT.mkdir(exist_ok=True)

pothole = Image.open(ASSETS / "pothole-evidence.png").convert("RGB")
crack = Image.open(ASSETS / "crack-night-evidence.png").convert("RGB")

pothole.save(OUTPUT / "known_pothole_01.jpg", quality=92)
ImageOps.mirror(pothole).save(OUTPUT / "known_pothole_02.jpg", quality=92)
crack.save(OUTPUT / "known_crack_01.jpg", quality=92)
crack.save(OUTPUT / "night_road_01.jpg", quality=92)

# clean_road_01.jpg is checked into the fixture directory separately because
# it was selected only after both packaged models returned zero detections.

blurred = pothole.resize((48, 36)).resize((640, 480)).filter(ImageFilter.GaussianBlur(16))
blurred.save(OUTPUT / "invalid_blurry_01.jpg", quality=80)

print(f"Created fixtures in {OUTPUT}")
