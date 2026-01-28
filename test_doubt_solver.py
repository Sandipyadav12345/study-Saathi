"""
Day 8 Verification: AI Doubt Solver
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_doubt_solver():
    print("🔹 Testing AI Doubt Solver (Day 8)...")
    
    # 1. English Test
    print("\n1. Asking 'What is photosynthesis?' (English)...")
    try:
        payload = {"doubt": "What is photosynthesis?", "mode": "english"}
        resp = requests.post(f"{BASE_URL}/api/ai/solve-doubt", json=payload)
        data = resp.json()
        
        if resp.status_code == 200:
            print(f"✅ AI Response: '{data.get('answer')[:100]}...'")
        else:
            print(f"❌ FAIL: {resp.text}")
            
    except Exception as e:
        print(f"❌ FAIL: {e}")

    # 2. Hinglish Test
    print("\n2. Asking 'Gravity kaise kaam karta hai?' (Hinglish)...")
    try:
        payload = {"doubt": "Gravity kaise kaam karta hai?", "mode": "hinglish"}
        resp = requests.post(f"{BASE_URL}/api/ai/solve-doubt", json=payload)
        data = resp.json()
        
        if resp.status_code == 200:
            print(f"✅ AI Response: '{data.get('answer')[:100]}...'")
        else:
            print(f"❌ FAIL: {resp.text}")
            
    except Exception as e:
        print(f"❌ FAIL: {e}")

if __name__ == "__main__":
    test_doubt_solver()
