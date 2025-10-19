#!/usr/bin/env python3
"""
Environment Setup for KcartBot Image Generation
Sets up free API keys and dependencies
"""

import os
import subprocess
import sys

def setup_environment():
    """Setup the environment for KcartBot image generation."""
    
    print("🛠️  Setting up KcartBot Image Generation Environment")
    print("=" * 50)
    
    # Create necessary directories
    directories = [
        "data/generated_images",
        "src/chatbot",
        "demos"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# FREE Image Generation APIs
# Get free API keys from:
# Hugging Face: https://huggingface.co/settings/tokens
# Unsplash: https://unsplash.com/developers

HUGGINGFACE_TOKEN=your_free_huggingface_token_here
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here

# Image Generation Settings
IMAGE_GENERATION_ENABLED=true
DEFAULT_IMAGE_API=huggingface

# Application Settings
DEBUG=true
""")
        print("✅ Created .env file - Please update with your FREE API keys")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Please run: pip install -r requirements.txt")
    
    print("\n🎉 Environment setup completed!")
    print("\n📝 Next steps:")
    print("1. Get FREE API keys:")
    print("   - Hugging Face: https://huggingface.co/settings/tokens")
    print("   - Unsplash: https://unsplash.com/developers")
    print("2. Update .env file with your keys")
    print("3. Run: python demos/demo_image_generation.py")
    print("4. Test the image generation!")

if __name__ == "__main__":
    setup_environment()