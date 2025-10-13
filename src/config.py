import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for easier setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kcartbot.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Note: GEMINI_API_KEY is optional at app startup; specific features may require it

print(f"Using database: {DATABASE_URL}")