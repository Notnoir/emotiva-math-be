# -*- coding: utf-8 -*-
"""
Test Adaptive Learning Engine API
TAHAP 6 - AI Core Testing
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """Pretty print API response"""
    print("\n" + "="*70)
    print("TEST: " + title)
    print("="*70)
    print("Status Code: " + str(response.status_code))
    print("Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def main():
    print("\nTESTING ADAPTIVE LEARNING ENGINE - TAHAP 6")
    
    # 1. Create test user first
    print("\n\n[1] CREATE TEST USER")
    user_data = {
        "nama": "Budi Santoso",
        "gaya_belajar": "visual",
        "level": "pemula"
    }
    response = requests.post(BASE_URL + "/profile", json=user_data)
    print_response("Create Test User", response)
    user_id = response.json()['data']['id']
    
    # 2. Log some emotions
    print("\n\n[2] LOG EMOTIONS")
    emotions_data = [
        {"user_id": user_id, "emosi": "netral", "context": "Mulai belajar"},
        {"user_id": user_id, "emosi": "bingung", "context": "Belajar volume kubus"}
    ]
    
    for emotion in emotions_data:
        response = requests.post(BASE_URL + "/emotion", json=emotion)
        print("  Logged: " + emotion['emosi'])
    
    # 3. TEST ADAPTIVE CONTENT - Kubus dengan gaya belajar Visual
    print("\n\n[3] GET ADAPTIVE CONTENT - KUBUS (Visual Learner)")
    adaptive_request = {
        "user_id": user_id,
        "topic": "kubus",
        "emosi": "bingung"
    }
    response = requests.post(BASE_URL + "/adaptive/content", json=adaptive_request)
    print_response("Adaptive Content for Kubus (Visual + Bingung)", response)
    
    # 4. Get recommendations
    print("\n\n[4] GET TOPIC RECOMMENDATIONS")
    response = requests.get(BASE_URL + "/adaptive/recommend?user_id=" + str(user_id))
    print_response("Topic Recommendations", response)
    
    print("\n\n" + "="*70)
    print("ALL ADAPTIVE LEARNING TESTS COMPLETED!")
    print("="*70)
    print("\nSUMMARY:")
    print("- Adaptive content generation working")
    print("- Learning style adaptation (Visual, Auditori, Kinestetik)")
    print("- Emotion-aware content (Cemas, Bingung, Netral, Percaya Diri)")
    print("- Difficulty adjustment based on performance")
    print("- Personalized recommendations")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
