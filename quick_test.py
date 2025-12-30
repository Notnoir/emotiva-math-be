# -*- coding: utf-8 -*-
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Create user
user_data = {"nama": "Test LLM", "gaya_belajar": "visual", "level": "pemula"}
r = requests.post(BASE_URL + "/profile", json=user_data)
user_id = r.json()['data']['id']

# Request adaptive content
adaptive_request = {
    "user_id": user_id,
    "topic": "kubus",
    "emosi": "bingung"
}

response = requests.post(BASE_URL + "/adaptive/content", json=adaptive_request)
data = response.json()

# Save to file for inspection
with open('llm_output.txt', 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("LLM OUTPUT TEST\n")
    f.write("="*70 + "\n\n")
    
    explanation = data['data']['content']['explanation']
    
    f.write("FULL EXPLANATION:\n")
    f.write("-"*70 + "\n")
    f.write(explanation)
    f.write("\n" + "-"*70 + "\n\n")
    
    f.write("METADATA:\n")
    f.write(f"Difficulty: {data['data']['difficulty']}\n")
    f.write(f"Topic: {data['data']['topic_name']}\n")
    f.write(f"Learning Style: {data['data']['learning_style']}\n\n")
    
    f.write("MOTIVATION:\n")
    f.write(f"{data['data']['motivation']}\n\n")
    
    # Check LLM usage
    f.write("="*70 + "\n")
    f.write("LLM STATUS:\n")
    f.write("="*70 + "\n")
    
    if "Halo" in explanation or "hai" in explanation.lower() or "Oke" in explanation or "Okay" in explanation:
        f.write("✅ LLM IS ACTIVE!\n")
        f.write("Content shows natural, conversational language.\n")
    elif "KUBUS - Penjelasan" in explanation or "**KUBUS" in explanation:
        f.write("⚠️  LLM NOT ACTIVE - Using template fallback\n")
    else:
        f.write("Check manually\n")

print("Output saved to llm_output.txt")
print("\nPreview:")
print(explanation[:200] + "...")
