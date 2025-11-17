#!/usr/bin/env python3
"""
Simple build script for creating an itch.io HTML5 build using pygbag
"""

import subprocess
import sys
import os

def build():
    """Build the game for itch.io"""
    
    print("=" * 60)
    print("Building Scoundrel for itch.io (HTML5)")
    print("=" * 60)
    
    # Simple pygbag command - just archive mode
    # This will bundle everything: code/, assets/, and all subdirectories
    cmd = [
        sys.executable, "-m", "pygbag",
        "--archive",  # Create build without running server
        "main.py"  # Point to your main.py in the code folder
    ]
    
    print("\n📦 Running pygbag build...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        
        # Check what was created
        if os.path.exists('build'):
            print("\n📁 Files created in 'build/' folder:")
            for item in os.listdir('build'):
                print(f"   • {item}")
            
            print("\n📤 TO UPLOAD TO ITCH.IO:")
            print("   1. Go into the 'build/' folder")
            print("   2. Select ALL files inside (not the folder itself)")
            print("   3. Create a ZIP of those files")
            print("   4. Upload to itch.io as HTML project")
            print("   5. Set viewport to 1222x686")
            print("   6. Enable 'This file will be played in the browser'")
            
        elif os.path.exists('dist'):
            print("\n📁 Files created in 'dist/' folder:")
            for item in os.listdir('dist'):
                print(f"   • {item}")
            
            print("\n📤 TO UPLOAD TO ITCH.IO:")
            print("   1. Go into the 'dist/' folder")
            print("   2. Select ALL files inside (not the folder itself)")
            print("   3. Create a ZIP of those files")
            print("   4. Upload to itch.io as HTML project")
            print("   5. Set viewport to 1222x686")
            print("   6. Enable 'This file will be played in the browser'")
        
        print("\n" + "=" * 60)
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Make sure pygbag is installed: pip install pygbag")
        print("   2. Make sure you're in the game directory")
        print("   3. Make sure main.py has async/await support")
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)