"""
Test script untuk EMOTIVA-MATH API
TAHAP 2 - Database & Learning Profile
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def main():
    print("\n🚀 TESTING EMOTIVA-MATH API - TAHAP 2")
    
    # 1. Create User Profile
    print("\n\n1️⃣ CREATE USER PROFILE")
    user_data = {
        "nama": "Andi Pratama",
        "gaya_belajar": "visual",
        "level": "pemula"
    }
    response = requests.post(f"{BASE_URL}/profile", json=user_data)
    print_response("Create User Profile", response)
    user_id = response.json()['data']['id']
    
    # 2. Get All Profiles
    print("\n\n2️⃣ GET ALL PROFILES")
    response = requests.get(f"{BASE_URL}/profile")
    print_response("Get All Profiles", response)
    
    # 3. Get Specific Profile
    print(f"\n\n3️⃣ GET PROFILE ID {user_id}")
    response = requests.get(f"{BASE_URL}/profile/{user_id}")
    print_response(f"Get Profile {user_id}", response)
    
    # 4. Update Profile
    print(f"\n\n4️⃣ UPDATE PROFILE ID {user_id}")
    update_data = {
        "level": "menengah"
    }
    response = requests.put(f"{BASE_URL}/profile/{user_id}", json=update_data)
    print_response("Update Profile", response)
    
    # 5. Log Emotion
    print(f"\n\n5️⃣ LOG EMOTION")
    emotion_data = {
        "user_id": user_id,
        "emosi": "percaya_diri",
        "context": "Setelah menyelesaikan quiz Kubus"
    }
    response = requests.post(f"{BASE_URL}/emotion", json=emotion_data)
    print_response("Log Emotion", response)
    
    # Log another emotion
    emotion_data2 = {
        "user_id": user_id,
        "emosi": "bingung",
        "context": "Saat mempelajari volume Tabung"
    }
    response = requests.post(f"{BASE_URL}/emotion", json=emotion_data2)
    print_response("Log Emotion (2)", response)
    
    # 6. Get Emotion History
    print(f"\n\n6️⃣ GET EMOTION HISTORY")
    response = requests.get(f"{BASE_URL}/emotion/{user_id}")
    print_response(f"Emotion History for User {user_id}", response)
    
    # 7. Create Learning Log
    print(f"\n\n7️⃣ CREATE LEARNING LOG")
    log_data = {
        "materi": "Kubus - Volume dan Luas Permukaan",
        "tipe_aktivitas": "belajar",
        "durasi": 300
    }
    response = requests.post(f"{BASE_URL}/learning-logs/{user_id}", json=log_data)
    print_response("Create Learning Log", response)
    
    # Create quiz log
    quiz_data = {
        "materi": "Quiz Kubus",
        "tipe_aktivitas": "quiz",
        "skor": 85,
        "durasi": 120
    }
    response = requests.post(f"{BASE_URL}/learning-logs/{user_id}", json=quiz_data)
    print_response("Create Quiz Log", response)
    
    # 8. Get Learning Logs
    print(f"\n\n8️⃣ GET LEARNING LOGS")
    response = requests.get(f"{BASE_URL}/learning-logs/{user_id}")
    print_response(f"Learning Logs for User {user_id}", response)
    
    # 9. Get Updated Profile with Stats
    print(f"\n\n9️⃣ GET UPDATED PROFILE WITH STATS")
    response = requests.get(f"{BASE_URL}/profile/{user_id}")
    print_response(f"Updated Profile with Stats", response)
    
    print("\n\n" + "="*60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
