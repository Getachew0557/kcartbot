#!/usr/bin/env python3
"""
Verify API Tokens for KcartBot Image Generation
Check if your FREE API tokens are working correctly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_huggingface_token():
    """Check if Hugging Face token is valid."""
    token = os.getenv("HUGGINGFACE_TOKEN")
    
    print("\n🔍 Checking Hugging Face Token...")
    
    if not token or token == "your_free_huggingface_token_here":
        print("❌ Hugging Face Token: NOT SET")
        print("   Please set HUGGINGFACE_TOKEN in your .env file")
        return False
    
    # Test token by making a simple API call
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            "https://huggingface.co/api/whoami",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Hugging Face Token: VALID")
            print(f"   👤 User: {user_info.get('name', 'Unknown')}")
            print(f"   🔑 Token: {token[:10]}...{token[-10:]}")
            print(f"   📧 Email: {user_info.get('email', 'Not provided')}")
            return True
        else:
            print(f"❌ Hugging Face Token: INVALID (Error {response.status_code})")
            print(f"   📝 Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Hugging Face Token: ERROR - {e}")
        return False

def check_unsplash_key():
    """Check if Unsplash key is valid."""
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    
    print("\n🔍 Checking Unsplash Access Key...")
    
    if not key or key == "your_unsplash_access_key_here":
        print("❌ Unsplash Access Key: NOT SET")
        print("   Please set UNSPLASH_ACCESS_KEY in your .env file")
        return False
    
    try:
        response = requests.get(
            f"https://api.unsplash.com/photos/random?client_id={key}&query=test",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Unsplash Access Key: VALID")
            print(f"   🔑 Key: {key[:10]}...{key[-10:]}")
            print(f"   📷 Photo by: {data.get('user', {}).get('name', 'Unknown')}")
            print(f"   📊 Remaining requests: {response.headers.get('X-Ratelimit-Remaining', 'Unknown')}")
            return True
        else:
            print(f"❌ Unsplash Access Key: INVALID (Error {response.status_code})")
            print(f"   📝 Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Unsplash Access Key: ERROR - {e}")
        return False

def main():
    print("🔐 KcartBot API Token Verification")
    print("=" * 60)
    
    hf_valid = check_huggingface_token()
    unsplash_valid = check_unsplash_key()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"   🤗 Hugging Face: {'✅ WORKING' if hf_valid else '❌ NOT WORKING'}")
    print(f"   📸 Unsplash: {'✅ WORKING' if unsplash_valid else '❌ NOT WORKING'}")
    
    if not hf_valid:
        print("\n💡 Hugging Face Fix Instructions:")
        print("1. 🌐 Go to: https://huggingface.co/settings/tokens")
        print("2. ➕ Click 'New token'")
        print("3. 📝 Name: 'kcartbot-image-gen'")
        print("4. ⚡ Role: Select 'Write' (NOT 'Read')")
        print("5. 📋 Copy the new token")
        print("6. 🔧 Update .env file: HUGGINGFACE_TOKEN=your_new_token_here")
    
    if not unsplash_valid:
        print("\n💡 Unsplash Fix Instructions:")
        print("1. 🌐 Go to: https://unsplash.com/developers")
        print("2. 📝 Register as developer")
        print("3. 🚀 Create New Application")
        print("4. 🔑 Copy the Access Key")
        print("5. 🔧 Update .env file: UNSPLASH_ACCESS_KEY=your_access_key_here")
    
    if hf_valid and unsplash_valid:
        print("\n🎉 All API tokens are working perfectly!")
        print("🚀 You're ready to generate high-quality images!")
    elif not hf_valid and not unsplash_valid:
        print("\n⚠️  No API tokens configured. The system will use fallback SVG images.")
        print("💡 Consider getting FREE API keys for better image quality.")
    else:
        print("\n✅ Partial setup complete. Some features will work with fallbacks.")

if __name__ == "__main__":
    main()