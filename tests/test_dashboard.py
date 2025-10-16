"""Simple test script to verify KcartBot dashboard is working."""

import requests
import time

def test_dashboard():
    """Test if the dashboard is accessible."""
    print("🌱 Testing KcartBot Dashboard...")
    
    try:
        # Test if Streamlit is running
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running successfully!")
            print("🌐 Open your browser and go to: http://localhost:8501")
            print("\n🎯 Dashboard Features:")
            print("• 💬 Chat Interface - Talk to KcartBot AI")
            print("• 📊 Analytics - View charts and statistics")
            print("• 🛒 Products - Browse Ethiopian agricultural products")
            print("• 📦 Orders - Manage order history")
            print("• 🧠 Knowledge Base - Search product information")
            print("\n🚀 Try these sample conversations:")
            print("• 'I want to order some tomatoes'")
            print("• 'How should I store avocados?'")
            print("• 'What's the price of red onions?'")
            print("• 'I'm a supplier, I want to register'")
            return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Dashboard is not running. Please start it with: streamlit run dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    test_dashboard()
