#!/usr/bin/env python
"""
Verification script to check if all required translation modules are present
"""
import os
import sys

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (MISSING)")
        return False

def main():
    """Check all required translation modules"""
    print("Verifying Translation Modules")
    print("=" * 50)
    
    frontend_path = os.path.join("frontend", "lnd-nexus", "app")
    
    if not os.path.exists(frontend_path):
        print(f"✗ Frontend directory not found: {frontend_path}")
        return False
    
    # Check required translation modules
    required_files = [
        (os.path.join(frontend_path, "lib", "translate.ts"), "Translation utilities"),
        (os.path.join(frontend_path, "lib", "imageTranslate.ts"), "Image translation utilities"),
        (os.path.join(frontend_path, "lib", "translationMemory.ts"), "Translation memory system"),
        (os.path.join(frontend_path, "components", "LanguageSwitcher.tsx"), "Language switcher component"),
    ]
    
    all_present = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    print("\n" + "=" * 50)
    if all_present:
        print("✓ All translation modules are present!")
        return True
    else:
        print("✗ Some translation modules are missing!")
        print("\nTo fix this, run the setup script again or manually create the missing files.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 