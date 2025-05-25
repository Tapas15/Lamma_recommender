import sys
import os
import json

# Add current directory to path
sys.path.append('.')

# Import language middleware
from backend.utils.language_middleware import (
    get_translation, 
    get_image_translation, 
    add_translation,
    add_image_translation
)

# Test translations
print("Testing language functionality...")

# Add some translations
print("\nAdding translations...")
add_translation("welcome", "Welcome to the Job Recommender API", "en")
add_translation("welcome", "مرحبًا بك في واجهة برمجة تطبيقات توصية الوظائف", "ar")

# Add some image translations
print("\nAdding image translations...")
add_image_translation("logo", "/images/en/logo.png", "en")
add_image_translation("logo", "/images/ar/logo.png", "ar")

# Get translations
print("\nGetting translations...")
print(f"English welcome: {get_translation('welcome', 'en')}")
print(f"Arabic welcome: {get_translation('welcome', 'ar')}")

# Get image translations
print("\nGetting image translations...")
print(f"English logo: {get_image_translation('logo', 'en')}")
print(f"Arabic logo: {get_image_translation('logo', 'ar')}")

# Check translation files
print("\nChecking translation files...")
translations_dir = os.path.join("backend", "utils", "translations")
for filename in os.listdir(translations_dir):
    filepath = os.path.join(translations_dir, filename)
    print(f"\nContents of {filename}:")
    with open(filepath, "r", encoding="utf-8") as f:
        content = json.load(f)
        print(json.dumps(content, indent=2, ensure_ascii=False))

print("\nLanguage functionality test completed!") 