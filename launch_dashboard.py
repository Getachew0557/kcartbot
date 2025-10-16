"""KcartBot Launcher Script"""

import subprocess
import sys
import os
import webbrowser
import time

def launch_dashboard():
    """Launch the KcartBot dashboard."""
    print("🌱 KcartBot Dashboard Launcher")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('kcartbot.db'):
        print("❌ Database not found. Generating data first...")
        try:
            subprocess.run([sys.executable, 'data/generate_data.py'], check=True)
            print("✅ Data generated successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating data: {e}")
            return
    
    print("🚀 Starting KcartBot Dashboard...")
    print("📊 Dashboard will open in your browser at: http://localhost:8501")
    print("💬 You can interact with the AI chatbot through the web interface")
    print("📈 View analytics, manage products, and explore the knowledge base")
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'dashboard.py'])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thank you for using KcartBot!")

if __name__ == "__main__":
    launch_dashboard()

