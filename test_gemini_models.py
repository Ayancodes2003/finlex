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
    
    # List available models
    try:
        print("Available models:")
        for model in genai.list_models():
            print(f"  - {model.name}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        
    # Try different model names
    model_names = ['gemini-pro', 'gemini-1.0-pro', 'gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.0-pro']
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, world!")
            print(f"✅ Model '{model_name}' is working correctly")
            print(f"Response: {response.text[:100]}...")
            break
        except Exception as e:
            print(f"❌ Model '{model_name}' failed: {str(e)}")
else:
    print("❌ Gemini API key not found")