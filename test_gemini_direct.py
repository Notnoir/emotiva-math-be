"""
Direct test Google Gemini API
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
use_llm = os.getenv('USE_LLM', 'False').lower() == 'true'

print("="*70)
print("GEMINI API TEST")
print("="*70)

print(f"\nUSE_LLM setting: {use_llm}")
print(f"API Key present: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    print(f"API Key length: {len(api_key)} characters")

print("\n" + "-"*70)
print("Testing API connection...")
print("-"*70)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # Simple test
    response = model.generate_content("Say 'Hello from Gemini!' in one sentence.")
    
    print("\n✅ SUCCESS! LLM is working!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. API key is invalid")
    print("2. API key doesn't have correct format")
    print("3. Network/firewall blocking connection")
    print("4. Gemini API quota exceeded")
    
print("\n" + "="*70)
