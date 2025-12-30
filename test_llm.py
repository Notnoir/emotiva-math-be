# -*- coding: utf-8 -*-
"""
Test LLM Integration
Quick test untuk verify LLM working
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

print("\n" + "="*70)
print("TESTING LLM INTEGRATION")
print("="*70)

# 1. Create test user
print("\n[1] Creating test user...")
user_data = {
    "nama": "Test User LLM",
    "gaya_belajar": "visual",
    "level": "pemula"
}
response = requests.post(BASE_URL + "/profile", json=user_data)
if response.status_code == 201:
    user_id = response.json()['data']['id']
    print(f"   User created! ID: {user_id}")
else:
    print("   Error creating user")
    exit(1)

# 2. Request adaptive content
print("\n[2] Requesting adaptive content with LLM...")
print("   Topic: Kubus")
print("   Learning Style: Visual")
print("   Emotion: Bingung")

adaptive_request = {
    "user_id": user_id,
    "topic": "kubus",
    "emosi": "bingung"
}

response = requests.post(BASE_URL + "/adaptive/content", json=adaptive_request)

if response.status_code == 200:
    data = response.json()
    
    print("\n" + "="*70)
    print("RESULT - ADAPTIVE CONTENT")
    print("="*70)
    
    explanation = data['data']['content']['explanation']
    
    print("\n📖 EXPLANATION (first 500 chars):")
    print("-" * 70)
    print(explanation[:500])
    print("...")
    print("-" * 70)
    
    print("\n📊 METADATA:")
    print(f"   Difficulty: {data['data']['difficulty']}")
    print(f"   Learning Style: {data['data']['learning_style']}")
    print(f"   Topic: {data['data']['topic_name']}")
    
    print("\n💬 MOTIVATION:")
    print(f"   {data['data']['motivation']}")
    
    # Check if LLM was used
    print("\n" + "="*70)
    print("LLM STATUS CHECK")
    print("="*70)
    
    # Indicators that LLM was used:
    # - Natural conversational language
    # - Not exactly matching template
    # - Personalized greeting
    # - Adaptive tone
    
    if "Halo" in explanation or "hai" in explanation.lower() or "Oke" in explanation:
        print("✅ LLM ACTIVE - Content is conversational and natural!")
        print("   (Contains natural greetings/conversational words)")
    elif "KUBUS - Penjelasan" in explanation:
        print("⚠️  LLM INACTIVE - Using template-based content")
        print("   (Template format detected)")
    else:
        print("❓ UNCERTAIN - Check content manually")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)
    
else:
    print(f"   Error: {response.status_code}")
    print(f"   Response: {response.text}")
