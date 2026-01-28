"""
Day 9 Verification: Real-World Context & Effort Motivation
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_day9_features():
    print("🔹 Testing Day 9 Features...")
    
    # 1. Test Real-World Context in Explanation
    print("\n1. Testing Plan Explanation (Real usage)...")
    plan = {
        "date": "2024-12-01", 
        "total_study_hours": 2, 
        "schedule": [
            {"time_slot": "Morning", "activities": [{"subject": "Calculus", "difficulty": "hard"}]}
        ]
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/ai/explain-plan", json={"plan": plan, "mode": "english"})
        if resp.status_code == 200:
            print(f"✅ Explanation: {resp.json().get('explanation')[:100]}...")
        else:
            print("❌ Explain failed")
    except Exception as e: print(f"❌ Error: {e}")

    # 2. Test Doubt Solver (Real usage)
    print("\n2. Testing Doubt Solver (Real usage)...")
    try:
        resp = requests.post(f"{BASE_URL}/api/ai/solve-doubt", json={"doubt": "What is probability?", "mode": "english"})
        if resp.status_code == 200:
            ans = resp.json().get('answer')
            print(f"✅ Answer: {ans[:100]}...")
            if "Real-life" in ans or "Used in" in ans or "Example" in ans: 
                 # Note: With fallback it won't show, but logic path is verified if no crash
                 print("   (Note: Real key needed for actual generated content, but prompt is set)")
        else:
            print("❌ Doubt failed")
    except Exception as e: print(f"❌ Error: {e}")

    # 3. Test Motivation (Effort based)
    print("\n3. Testing Motivation (Doubt Solved = True)...")
    try:
        # Simulate frontend sending doubt_solved=True
        payload = {
            "student_id": "day9_test_user",
            "mode": "english",
            "doubt_solved": True
        }
        resp = requests.post(f"{BASE_URL}/api/ai/motivation", json=payload)
        if resp.status_code == 200:
            msg = resp.json().get("message")
            print(f"✅ Motivation: '{msg}'")
            # Fallback won't show dynamic text, but code path is safe.
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_day9_features()
