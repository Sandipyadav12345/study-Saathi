"""
Test script for Study Saathi API
Run this after starting the server with: python app.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("1. Testing Health Check Endpoint")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running?")
        print("   Start the server with: python app.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_test_endpoint():
    """Test the test endpoint with sample data"""
    print("\n" + "="*50)
    print("2. Testing Test Endpoint (GET /api/plan/test)")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/api/plan/test", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        if 'plan' in data:
            plan = data['plan']
            print(f"Date: {plan.get('date')}")
            print(f"Total Study Hours: {plan.get('total_study_hours')}")
            print(f"Time Slots Used: {plan.get('summary', {}).get('time_slots_used', 0)}")
            print(f"Subjects Count: {plan.get('summary', {}).get('subjects_count', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_daily_plan():
    """Test daily plan generation"""
    print("\n" + "="*50)
    print("3. Testing Daily Plan Endpoint (POST /api/plan/daily)")
    print("="*50)
    
    test_data = {
        "subjects": [
            {
                "name": "Mathematics",
                "exam_date": "2024-12-20",
                "difficulty": "hard",
                "topics": ["Calculus", "Linear Algebra"]
            },
            {
                "name": "Physics",
                "exam_date": "2024-12-18",
                "difficulty": "medium",
                "topics": ["Mechanics", "Thermodynamics"]
            },
            {
                "name": "Chemistry",
                "exam_date": "2024-12-25",
                "difficulty": "easy",
                "topics": ["Organic Chemistry"]
            }
        ],
        "daily_hours": 6.0,
        "free_time_slots": [
            {"start": "09:00", "end": "11:00", "label": "Morning"},
            {"start": "14:00", "end": "16:00", "label": "Afternoon"},
            {"start": "17:00", "end": "19:00", "label": "Evening"}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/plan/daily",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"[OK] Success: {data.get('success', False)}")
            if 'plan' in data:
                plan = data['plan']
                print(f"Date: {plan.get('date')}")
                print(f"Total Study Hours: {plan.get('total_study_hours')}")
                print(f"\nSchedule:")
                for slot in plan.get('schedule', []):
                    print(f"  - {slot.get('time_slot')}: {slot.get('slot_start')} to {slot.get('slot_end')}")
                    for activity in slot.get('activities', []):
                        print(f"    * {activity.get('subject')}: {activity.get('start_time')}-{activity.get('end_time')} ({activity.get('duration_hours')}h)")
        else:
            print(f"[ERROR] Error: {data.get('error', 'Unknown error')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_weekly_plan():
    """Test weekly plan generation"""
    print("\n" + "="*50)
    print("4. Testing Weekly Plan Endpoint (POST /api/plan/weekly)")
    print("="*50)
    
    test_data = {
        "subjects": [
            {
                "name": "Data Structures",
                "exam_date": "2024-12-20",
                "difficulty": "hard"
            },
            {
                "name": "Operating Systems",
                "exam_date": "2024-12-18",
                "difficulty": "medium"
            }
        ],
        "daily_hours": 6.0,
        "start_date": "2024-12-01"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/plan/weekly",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"[OK] Success: {data.get('success', False)}")
            if 'plan' in data:
                plan = data['plan']
                print(f"Week: {plan.get('week_start')} to {plan.get('week_end')}")
                print(f"Daily Hours: {plan.get('daily_hours')}")
                print(f"Total Subjects: {plan.get('summary', {}).get('total_subjects', 0)}")
                print(f"Total Study Hours (Week): {plan.get('summary', {}).get('total_study_hours_week', 0)}")
                print(f"Days in plan: {len(plan.get('days', []))}")
        else:
            print(f"[ERROR] Error: {data.get('error', 'Unknown error')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_error_handling():
    """Test error handling with invalid data"""
    print("\n" + "="*50)
    print("5. Testing Error Handling")
    print("="*50)
    
    # Test with missing subjects
    try:
        response = requests.post(
            f"{BASE_URL}/api/plan/daily",
            json={"daily_hours": 6.0},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if response.status_code == 400:
            print(f"[OK] Correctly returned error: {data.get('error')}")
            return True
        else:
            print(f"[ERROR] Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("STUDY SAATHI API TEST SUITE")
    print("="*50)
    
    print("\n[INFO] Waiting for server to be ready...")
    time.sleep(3)  # Wait for server to start
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Test Endpoint", test_test_endpoint()))
    results.append(("Daily Plan", test_daily_plan()))
    results.append(("Weekly Plan", test_weekly_plan()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! API is working correctly!")
    else:
        print("\n[WARNING] Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
