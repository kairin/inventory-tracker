#!/usr/bin/env python3

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_uv_installed():
    """Check if uv is installed."""
    return shutil.which("uv") is not None

def install_uv():
    """Install uv if not present."""
    print("📦 Installing uv (Python package manager)...")
    try:
        # Install uv using the official installer
        subprocess.check_call([
            "curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"
        ], shell=True)
        print("✅ uv installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install uv")
        print("💡 Please install uv manually: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def setup_project():
    """Set up the project using uv."""
    print("🔧 Setting up project with uv...")
    
    # Create pyproject.toml if it doesn't exist
    if not os.path.exists("pyproject.toml"):
        print("📝 Creating pyproject.toml...")
        pyproject_content = """[project]
name = "inventory-tracker"
version = "0.1.0"
description = "Simple inventory management with barcode scanning and image verification"
dependencies = [
    "textual>=0.45.0",
    "rich>=13.0.0",
    "docling>=1.0.0",
    "pillow>=10.0.0",
    "opencv-python>=4.8.0",
    "numpy>=1.24.0",
]
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
        with open("pyproject.toml", "w") as f:
            f.write(pyproject_content)
        print("✅ Created pyproject.toml")
    
    try:
        # Install dependencies using uv
        print("📦 Installing dependencies with uv...")
        subprocess.check_call(["uv", "sync"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies with uv")
        return False

def run_app():
    """Run the inventory tracker app using uv."""
    print("🚀 Starting Inventory Tracker...")
    try:
        subprocess.check_call(["uv", "run", "inventory_tracker.py"])
    except subprocess.CalledProcessError:
        print("❌ Failed to start inventory tracker")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

def main():
    """Main entry point."""
    if not check_uv_installed():
        print("⚠️  uv not found - installing...")
        if not install_uv():
            return
    
    if not setup_project():
        return
    
    run_app()

if __name__ == "__main__":
    main()