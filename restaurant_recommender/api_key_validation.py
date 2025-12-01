import os
import asyncio
from google import genai

async def validate_api_key():
    """Validate if the Google API key is valid by making a test call"""
    try:
        # Get the API key
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
        
        if not GOOGLE_API_KEY:
            print("❌ API Key Not Found: 'GOOGLE_API_KEY' environment variable is not set.")
            return False
        
        # Create a client with the API key
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        # Make a test call to validate the key
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'API key is valid' in one word."
        )
        
        if response and response.text:
            print("✅ Gemini API key is valid!")
            return True
        else:
            print("❌ API Key Validation Failed: No response from API.")
            return False
            
    except Exception as e:
        print(f"❌ Authentication Error: {e}")
        print("🔑 Please make sure you have added 'GOOGLE_API_KEY' to your environment variables.")
        return False

if __name__ == "__main__":
    result = asyncio.run(validate_api_key())
    exit(0 if result else 1)