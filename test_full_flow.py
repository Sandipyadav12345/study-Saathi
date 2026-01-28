"""
Study Saathi - End-to-End Integration Test (Day 5)
Verifies the full flow: Plan -> Explain -> Action -> Motivate
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"🔹 {title}")
    print("="*60)

def step_1_generate_plan():
    print_section("STEP 1: Generate a Study Plan")
    
    payload = {
        "student_id": "test_user_day5",
        "subjects": [
            {"name": "Artificial Intelligence", "exam_date": "2024-12-25", "difficulty": "hard"},
            {"name": "Web Development", "exam_date": "2024-12-20", "difficulty": "medium"}
        ],
        "daily_hours": 5.0,
        "date": "2024-12-01"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/plan/daily", json=payload)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Plan Generated Successfully")
            print(f"   Plan ID: {data.get('plan_id')}")
            print(f"   Total Hours: {data.get('plan', {}).get('total_study_hours')}")
            return data.get("plan")
        else:
            print(f"❌ Failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def step_2_explain_plan(plan):
    print_section("STEP 2: Ask AI to Explain the Plan")
    
    if not plan:
        print("⚠️ Skipping (No Plan)")
        return

    payload = {
        "plan": plan,
        "mode": "english"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ai/explain-plan", json=payload)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ AI Explanation Received:")
            print(f"   \"{data.get('explanation')}\"")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def step_3_complete_tasks():
    print_section("STEP 3: Simulate Studying (Complete Tasks)")
    
    # Get today's tasks
    try:
        response = requests.get(f"{BASE_URL}/api/plan/today?student_id=test_user_day5")
        data = response.json()
        tasks = data.get("today_plan", [])
        
        if not tasks:
            print("⚠️ No tasks found to complete.")
            return
            
        # Complete the first 2 tasks
        for i, task in enumerate(tasks[:2]):
            task_id = task["task_id"]
            resp = requests.post(f"{BASE_URL}/api/task/complete/{task_id}?student_id=test_user_day5")
            if resp.status_code == 200:
                print(f"✅ Completed Task: {task['subject']} ({task['study_hours']}h)")
            else:
                print(f"❌ Failed to complete task {task_id}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def step_4_get_motivation():
    print_section("STEP 4: Get AI Motivation (Hinglish)")
    
    payload = {
        "student_id": "test_user_day5",
        "mode": "hinglish"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ai/motivation", json=payload)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ AI Motivation Received:")
            print(f"   \"{data.get('message')}\"")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 STARTING DAY 5 INTEGRATION TEST")
    
    # 1. Generate
    plan = step_1_generate_plan()
    
    # 2. Explain
    step_2_explain_plan(plan)
    
    # 3. Act
    step_3_complete_tasks()
    
    # 4. Motivate
    step_4_get_motivation()
    
    print("\n✅ TEST COMPLETE - The Backend is Alive!")

if __name__ == "__main__":
    main()
