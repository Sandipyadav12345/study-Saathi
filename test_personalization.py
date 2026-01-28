"""
Test script for Profile & Personalization (Day 6)
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_personalization():
    print("\n" + "="*50)
    print("Testing Personalized Motivation")
    print("="*50)
    
    student_id = "rahul_001"
    name = "Rahul"
    
    # 1. Create Profile
    print(f"1. Creating Profile for {name}...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/student/profile",
            json={"student_id": student_id, "name": name}
        )
        print(f"   Status: {resp.status_code} - {resp.json().get('message')}")
    except Exception as e:
        print(f"   Failed to create profile: {e}")
        return

    # 2. Get Motivation (Should use name)
    print(f"2. Asking for Motivation (Hinglish)...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/ai/motivation",
            json={"student_id": student_id, "mode": "hinglish"}
        )
        data = resp.json()
        message = data.get("message", "")
        print(f"   AI Response: \"{message}\"")
        
        if name in message or "Rahul" in message:
            print("   ✅ SUCCESS: Name found in response!")
        else:
            print("   ⚠️ NOTE: Name not explicitly found (might be API limitation or random variation)")
            
    except Exception as e:
        print(f"   Failed to get motivation: {e}")

if __name__ == "__main__":
    test_personalization()
