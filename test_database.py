"""
Test script for database functionality
Tests: plan saving, task completion, streak tracking
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_save_and_retrieve_plan():
    """Test saving a plan and retrieving it"""
    print("\n" + "="*50)
    print("1. Testing Save Plan & Retrieve Today's Plan")
    print("="*50)
    
    # Create a daily plan
    test_data = {
        "subjects": [
            {
                "name": "Mathematics",
                "exam_date": "2024-12-20",
                "difficulty": "hard",
                "topics": ["Calculus"]
            },
            {
                "name": "Physics",
                "exam_date": "2024-12-18",
                "difficulty": "medium"
            }
        ],
        "daily_hours": 6.0
    }
    
    try:
        # Save plan
        response = requests.post(
            f"{BASE_URL}/api/plan/daily",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Save Plan Status: {response.status_code}")
        save_data = response.json()
        print(f"Plan ID: {save_data.get('plan_id')}")
        
        # Get today's plan
        response = requests.get(f"{BASE_URL}/api/plan/today", timeout=5)
        print(f"Get Today Plan Status: {response.status_code}")
        today_data = response.json()
        
        if today_data.get("success"):
            tasks = today_data.get("today_plan", [])
            print(f"Total Tasks: {today_data.get('total_tasks')}")
            print(f"Completed Tasks: {today_data.get('completed_tasks')}")
            print(f"\nTasks:")
            for task in tasks[:3]:  # Show first 3
                print(f"  - {task.get('subject')}: {task.get('start_time')}-{task.get('end_time')} (Completed: {task.get('completed')})")
        
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_complete_task():
    """Test completing a task"""
    print("\n" + "="*50)
    print("2. Testing Task Completion")
    print("="*50)
    
    try:
        # Get today's plan first
        response = requests.get(f"{BASE_URL}/api/plan/today", timeout=5)
        today_data = response.json()
        tasks = today_data.get("today_plan", [])
        
        if not tasks:
            print("[WARNING] No tasks found. Create a plan first.")
            return False
        
        # Complete first task
        task_id = tasks[0].get("task_id")
        print(f"Completing task ID: {task_id}")
        
        response = requests.post(
            f"{BASE_URL}/api/task/complete/{task_id}",
            timeout=5
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data.get('message')}")
        
        # Verify it's completed
        response = requests.get(f"{BASE_URL}/api/plan/today", timeout=5)
        today_data = response.json()
        tasks = today_data.get("today_plan", [])
        completed = [t for t in tasks if t.get("task_id") == task_id]
        
        if completed and completed[0].get("completed"):
            print("[OK] Task successfully marked as completed!")
            return True
        else:
            print("[ERROR] Task not marked as completed")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_streak():
    """Test streak functionality"""
    print("\n" + "="*50)
    print("3. Testing Streak Tracking")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/streak", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get("success"):
            streak = data.get("streak", {})
            print(f"Current Streak: {streak.get('current_streak')} days")
            print(f"Longest Streak: {streak.get('longest_streak')} days")
            print(f"Last Study Date: {streak.get('last_study_date')}")
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_progress():
    """Test progress tracking"""
    print("\n" + "="*50)
    print("4. Testing Progress Tracking")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/progress", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get("success"):
            progress = data.get("progress", {})
            print(f"Date: {progress.get('date')}")
            print(f"Total Tasks: {progress.get('total_tasks')}")
            print(f"Completed Tasks: {progress.get('completed_tasks')}")
            print(f"Total Hours: {progress.get('total_hours')}")
            print(f"Completed Hours: {progress.get('completed_hours')}")
            print(f"Completion: {progress.get('completion_percentage')}%")
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run all database tests"""
    print("\n" + "="*50)
    print("DATABASE FUNCTIONALITY TEST SUITE")
    print("="*50)
    
    print("\n[INFO] Waiting for server to be ready...")
    time.sleep(2)
    
    results = []
    
    results.append(("Save & Retrieve Plan", test_save_and_retrieve_plan()))
    results.append(("Complete Task", test_complete_task()))
    results.append(("Streak Tracking", test_streak()))
    results.append(("Progress Tracking", test_progress()))
    
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
        print("\n[SUCCESS] All database tests passed!")
    else:
        print("\n[WARNING] Some tests failed.")

if __name__ == "__main__":
    main()
