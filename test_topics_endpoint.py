"""
Test endpoint /api/materials/topics
"""
import requests

def test_topics_endpoint():
    """Test GET /api/materials/topics"""
    
    print("\n" + "="*80)
    print("🧪 TEST: GET /api/materials/topics")
    print("="*80 + "\n")
    
    url = "http://localhost:5000/api/materials/topics"
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Status: {data['status']}")
            print(f"Count: {data['count']}")
            print()
            print("Available Topics:")
            print("-" * 80)
            
            for topic in data['data']:
                print(f"📚 {topic['title']} ({topic['id']})")
                print(f"   Description: {topic['description']}")
                print(f"   Difficulty: {topic['difficulty']}")
                print(f"   Color: {topic['color']}")
                print(f"   Icon: {topic['icon']}")
                print(f"   Materials: {topic['material_count']}")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running?")
        print("   Please start backend with: python run.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_topics_endpoint()
