#!/usr/bin/env python3
"""
Frontend Files Verification Script
Checks that all required frontend files are present and properly configured.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_frontend_files():
    """Check all required frontend files."""
    print("🔍 Verifying Frontend Files...")
    print("=" * 50)
    
    base_path = "frontend/lnd-nexus"
    all_good = True
    
    # Core configuration files
    files_to_check = [
        (f"{base_path}/package.json", "Package configuration"),
        (f"{base_path}/tsconfig.json", "TypeScript configuration"),
        (f"{base_path}/next.config.ts", "Next.js configuration"),
        (f"{base_path}/.env.local", "Environment variables"),
        (f"{base_path}/.gitignore", "Frontend gitignore"),
    ]
    
    # Translation library files
    lib_files = [
        (f"{base_path}/app/lib/utils.ts", "UI utilities (cn function)"),
        (f"{base_path}/app/lib/translate.ts", "Translation utilities"),
        (f"{base_path}/app/lib/imageTranslate.ts", "Image translation"),
        (f"{base_path}/app/lib/translationMemory.ts", "Translation memory"),
    ]
    
    # Key component files
    component_files = [
        (f"{base_path}/app/components/ui/button.tsx", "Button component"),
        (f"{base_path}/app/components/LanguageSwitcher.tsx", "Language switcher"),
        (f"{base_path}/app/components/TranslateButton.tsx", "Translate button"),
        (f"{base_path}/app/layout.tsx", "Root layout"),
        (f"{base_path}/app/page.tsx", "Home page"),
    ]
    
    print("\n📁 Core Configuration Files:")
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n📚 Translation Library Files:")
    for file_path, description in lib_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n🧩 Key Component Files:")
    for file_path, description in component_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All frontend files are present!")
        print("✅ Frontend should be working correctly now.")
    else:
        print("⚠️  Some files are missing. Please check the errors above.")
    
    return all_good

def check_git_tracking():
    """Check if important files are tracked by Git."""
    print("\n🔍 Checking Git Tracking...")
    print("=" * 50)
    
    import subprocess
    
    try:
        # Get list of tracked files
        result = subprocess.run(['git', 'ls-files'], 
                              capture_output=True, text=True, check=True)
        tracked_files = set(result.stdout.strip().split('\n'))
        
        important_files = [
            'frontend/lnd-nexus/app/lib/utils.ts',
            'frontend/lnd-nexus/app/lib/translate.ts',
            'frontend/lnd-nexus/app/lib/imageTranslate.ts',
            'frontend/lnd-nexus/app/lib/translationMemory.ts',
            'frontend/lnd-nexus/package.json',
            'frontend/lnd-nexus/tsconfig.json',
        ]
        
        all_tracked = True
        for file in important_files:
            if file in tracked_files:
                print(f"✅ Tracked: {file}")
            else:
                print(f"❌ Not tracked: {file}")
                all_tracked = False
        
        if all_tracked:
            print("🎉 All important files are tracked by Git!")
        else:
            print("⚠️  Some important files are not tracked by Git.")
            
    except subprocess.CalledProcessError:
        print("❌ Could not check Git status")

if __name__ == "__main__":
    print("Frontend Verification Script")
    print("=" * 50)
    
    # Change to project root if needed
    if not os.path.exists("frontend/lnd-nexus"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    files_ok = check_frontend_files()
    check_git_tracking()
    
    if files_ok:
        print("\n🚀 Frontend verification completed successfully!")
        print("You can now run the frontend with: npm run dev")
    else:
        print("\n❌ Frontend verification failed. Please fix the missing files.")
        sys.exit(1) 