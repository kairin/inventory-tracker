#!/usr/bin/env python3

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def main():
    """Main entry point."""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return
    
    print("📦 Installing dependencies...")
    if install_requirements():
        print("🚀 Starting Inventory Tracker...")
        try:
            from inventory_tracker import main as run_app
            run_app()
        except ImportError:
            print("❌ Failed to import inventory_tracker")

if __name__ == "__main__":
    main()