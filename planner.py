from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

DIFFICULTY_WEIGHT = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}

# Default time slots
DEFAULT_TIME_SLOTS = [
    {"start": "06:00", "end": "08:00", "label": "Morning"},
    {"start": "09:00", "end": "11:00", "label": "Late Morning"},
    {"start": "14:00", "end": "16:00", "label": "Afternoon"},
    {"start": "17:00", "end": "19:00", "label": "Evening"},
    {"start": "20:00", "end": "22:00", "label": "Night"}
]

def days_until_exam(exam_date: str) -> int:
    """Calculate days until exam date"""
    today = datetime.today().date()
    try:
        exam = datetime.strptime(exam_date, "%Y-%m-%d").date()
        return max((exam - today).days, 1)
    except ValueError:
        return 30 # Default safety

def calculate_priority_score(subject: Dict[str, Any]) -> float:
    """Calculate priority score based on difficulty and days until exam"""
    days_left = days_until_exam(subject["exam_date"])
    difficulty = subject.get("difficulty", "medium").lower()
    weight = DIFFICULTY_WEIGHT.get(difficulty, 2)
    
    # Higher priority for harder subjects and closer exams
    priority_score = (weight * 10) / days_left
    
    # Boost priority if exam is very close (within 7 days)
    if days_left <= 7:
        priority_score *= 1.5
    
    return round(priority_score, 2)

def allocate_time_slots(subjects: List[Dict[str, Any]], daily_hours: float) -> List[Dict[str, Any]]:
    """Allocate study time to subjects based on priority"""
    if not subjects:
        return []
    
    # Calculate priority for each subject
    plan = []
    for subject in subjects:
        priority = calculate_priority_score(subject)
        plan.append({
            "subject": subject["name"],
            "subject_id": subject.get("id", subject["name"].lower().replace(" ", "_")),
            "priority": priority,
            "difficulty": subject.get("difficulty", "medium"),
            "exam_date": subject["exam_date"],
            "days_until_exam": days_until_exam(subject["exam_date"]),
            "topics": subject.get("topics", []),
            "study_hours": 0  # Will be calculated
        })
    
    # Sort by priority (higher first)
    plan.sort(key=lambda x: x["priority"], reverse=True)
    
    # Allocate time proportionally based on priority
    total_priority = sum(item["priority"] for item in plan)
    
    if total_priority > 0:
        for item in plan:
            allocated_time = (item["priority"] / total_priority) * daily_hours
            item["study_hours"] = round(allocated_time, 2)
    
    return plan

def generate_daily_plan(subjects: List[Dict[str, Any]], daily_hours: float,
                       free_time_slots: List[Dict[str, str]] = None,
                       date: str = None) -> Dict[str, Any]:
    """Generate a detailed daily study plan with time slots and BREAKS"""
    
    if date is None:
        date = datetime.today().strftime("%Y-%m-%d")
    
    if free_time_slots is None:
        free_time_slots = DEFAULT_TIME_SLOTS
    
    # 1. Allocate hours per subject based on user input 'daily_hours'
    allocated_plan = allocate_time_slots(subjects, daily_hours)
    
    daily_schedule = []
    remaining_subjects = allocated_plan.copy()
    
    # Track how much we've scheduled to insert breaks
    BREAK_DURATION_MINS = 10
    
    for slot in free_time_slots:
        slot_start = datetime.strptime(slot["start"], "%H:%M")
        slot_end = datetime.strptime(slot["end"], "%H:%M")
        
        # Calculate total minutes in this slot
        slot_duration_mins = (slot_end - slot_start).total_seconds() / 60
        
        current_time_mins = 0
        slot_activities = []
        
        while current_time_mins < slot_duration_mins and remaining_subjects:
            # Pick the highest priority subject that still needs time
            # We round robin slightly or sticking to priority list is fine
            # Let's stick to the list order (Highest Priority First)
            
            subject = remaining_subjects[0]
            
            if subject["study_hours"] <= 0.1:
                remaining_subjects.pop(0)
                continue
                
            # Determine session length (e.g. max 60 mins per session before break)
            SESSION_MAX_MINS = 60
            time_available_mins = slot_duration_mins - current_time_mins
            
            # How much time does this subject need?
            needed_mins = subject["study_hours"] * 60
            
            actual_session_mins = min(needed_mins, SESSION_MAX_MINS, time_available_mins)
            
            if actual_session_mins < 10: 
                # Too small time slot, skip to next big slot or finish
                break
                
            # Add Study Activity
            start_ts = slot_start + timedelta(minutes=current_time_mins)
            end_ts = start_ts + timedelta(minutes=actual_session_mins)
            
            slot_activities.append({
                "subject": subject["subject"],
                "subject_id": subject["subject_id"],
                "type": "study",
                "duration_minutes": int(actual_session_mins),
                "start_time": start_ts.strftime("%H:%M"),
                "end_time": end_ts.strftime("%H:%M"),
                "difficulty": subject["difficulty"],
                "topics": subject.get("topics", [])
            })
            
            # Update counters
            subject["study_hours"] -= (actual_session_mins / 60)
            current_time_mins += actual_session_mins
            
            # Remove subject if done (or close enough)
            if subject["study_hours"] <= 0.1:
                if subject in remaining_subjects:
                    remaining_subjects.remove(subject)

            
            # Insert Break if there is time left
            if current_time_mins + BREAK_DURATION_MINS <= slot_duration_mins and subject["study_hours"] > 0:
                b_start = end_ts
                b_end = b_start + timedelta(minutes=BREAK_DURATION_MINS)
                
                slot_activities.append({
                    "subject": "Break",
                    "subject_id": "break",
                    "type": "break",
                    "duration_minutes": BREAK_DURATION_MINS,
                    "start_time": b_start.strftime("%H:%M"),
                    "end_time": b_end.strftime("%H:%M"),
                    "details": "Relax, stretch, drink water!"
                })
                current_time_mins += BREAK_DURATION_MINS

        if slot_activities:
            daily_schedule.append({
                "time_slot": slot["label"],
                "slot_start": slot["start"],
                "slot_end": slot["end"],
                "activities": slot_activities
            })

    # Summary
    unallocated = [s for s in remaining_subjects if s["study_hours"] > 0.1]
    
    return {
        "date": date,
        "total_study_hours": daily_hours,
        "schedule": daily_schedule,
        "summary": {
            "subjects_count": len(allocated_plan),
            "time_slots_used": len(daily_schedule),
            "unallocated_subjects": len(unallocated)
        },
        "subject_priorities": allocated_plan
    }
    
def generate_weekly_plan(subjects: List[Dict[str, Any]], daily_hours: float,
                         free_time_slots: List[Dict[str, str]] = None,
                         start_date: str = None) -> Dict[str, Any]:
    """Generate a weekly study plan"""
    if start_date is None:
        start_date = datetime.today().strftime("%Y-%m-%d")
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    weekly_plan = []
    
    for day_offset in range(7):
        current_date = (start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        day_plan = generate_daily_plan(subjects, daily_hours, free_time_slots, current_date)
        weekly_plan.append(day_plan)
    
    return {
        "week_start": start_date,
        "week_end": (start + timedelta(days=6)).strftime("%Y-%m-%d"),
        "daily_hours": daily_hours,
        "days": weekly_plan,
        "summary": {
            "total_subjects": len(subjects),
            "total_study_hours_week": daily_hours * 7
        }
    }

def validate_student_inputs(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate student input data"""
    if "subjects" not in data:
        return False, "Missing 'subjects' field"
    
    if not isinstance(data["subjects"], list) or len(data["subjects"]) == 0:
        return False, "'subjects' must be a non-empty list"
    
    if "daily_hours" not in data:
        # Default to 6 if not provided, allowing flexible inputs
        data["daily_hours"] = 6.0
    
    return True, "Valid"
