import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")
    
    # Test the model
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, world!")
        print("✅ Gemini API is working correctly")
        print(f"Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Error testing Gemini API: {str(e)}")
else:
    print("❌ Gemini API key not found")