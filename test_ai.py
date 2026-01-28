"""
Test script for AI endpoints
Run this after starting the server with: python app.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_explain_plan():
    print("\n" + "="*50)
    print("1. Testing Plan Explanation (English)")
    print("="*50)
    
    # Sample plan data (simplified)
    plan_data = {
        "date": "2024-12-01",
        "total_study_hours": 4.0,
        "schedule": [
             {
                 "time_slot": "Morning",
                 "activities": [{"subject": "Math", "difficulty": "hard"}]
             }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/explain-plan",
            json={"plan": plan_data, "mode": "english"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Explanation: {data.get('explanation')}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_motivation_hinglish():
    print("\n" + "="*50)
    print("2. Testing Motivation (Hinglish)")
    print("="*50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/motivation",
            json={"student_id": "default", "mode": "hinglish"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("AI TEST SUITE")
    test_explain_plan()
    test_motivation_hinglish()

if __name__ == "__main__":
    main()
