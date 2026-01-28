from flask import Flask, request, jsonify
from flask_cors import CORS
from planner import generate_daily_plan, generate_weekly_plan, validate_student_inputs
from datetime import datetime
from database import (
    init_db, save_study_plan, get_today_plan, complete_task,
    get_streak, get_daily_progress, create_student, get_student
)
from ai_service import generate_plan_explanation, generate_motivation, solve_doubt, generate_schedule_from_syllabus, generate_tutor_response
from file_service import read_file_content
import os
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize database on startup
init_db()


@app.route("/")
def home():
    return jsonify({
        "message": "Study Saathi API is running! 🎓",
        "endpoints": {
            "health": "/api/health",
            "daily_plan": "/api/plan/daily (POST)",
            "weekly_plan": "/api/plan/weekly (POST)"
        }
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Study Saathi API"
    })


@app.route("/api/plan/daily", methods=["POST"])
def create_daily_plan():
    """
    Generate a daily study plan
    
    Expected JSON body:
    {
        "subjects": [
            {
                "name": "Mathematics",
                "exam_date": "2024-12-15",
                "difficulty": "hard",
                "topics": ["Calculus", "Algebra"]
            }
        ],
        "daily_hours": 6.0,
        "free_time_slots": [
            {"start": "09:00", "end": "11:00", "label": "Morning"},
            {"start": "14:00", "end": "16:00", "label": "Afternoon"}
        ],
        "date": "2024-12-01"  # Optional, defaults to today
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate inputs
        is_valid, error_message = validate_student_inputs(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Extract parameters
        subjects = data["subjects"]
        daily_hours = float(data["daily_hours"])
        free_time_slots = data.get("free_time_slots")
        date = data.get("date")
        
        # Generate daily plan
        plan = generate_daily_plan(
            subjects=subjects,
            daily_hours=daily_hours,
            free_time_slots=free_time_slots,
            date=date
        )
        
        # Save plan to database
        student_id = data.get("student_id", "default")
        plan_id = save_study_plan(plan, plan_type="daily", student_id=student_id)
        
        return jsonify({
            "success": True,
            "plan": plan,
            "plan_id": plan_id,
            "message": "Daily study plan generated and saved successfully!"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to generate plan",
            "details": str(e)
        }), 500


@app.route("/api/plan/weekly", methods=["POST"])
def create_weekly_plan():
    """
    Generate a weekly study plan
    
    Expected JSON body:
    {
        "subjects": [
            {
                "name": "Mathematics",
                "exam_date": "2024-12-15",
                "difficulty": "hard",
                "topics": ["Calculus", "Algebra"]
            }
        ],
        "daily_hours": 6.0,
        "free_time_slots": [
            {"start": "09:00", "end": "11:00", "label": "Morning"},
            {"start": "14:00", "end": "16:00", "label": "Afternoon"}
        ],
        "start_date": "2024-12-01"  # Optional, defaults to today
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate inputs
        is_valid, error_message = validate_student_inputs(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Extract parameters
        subjects = data["subjects"]
        daily_hours = float(data["daily_hours"])
        free_time_slots = data.get("free_time_slots")
        start_date = data.get("start_date")
        
        # Generate weekly plan
        plan = generate_weekly_plan(
            subjects=subjects,
            daily_hours=daily_hours,
            free_time_slots=free_time_slots,
            start_date=start_date
        )
        
        # Save plan to database
        student_id = data.get("student_id", "default")
        plan_id = save_study_plan(plan, plan_type="weekly", student_id=student_id)
        
        return jsonify({
            "success": True,
            "plan": plan,
            "plan_id": plan_id,
            "message": "Weekly study plan generated and saved successfully!"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to generate plan",
            "details": str(e)
        }), 500


@app.route("/api/plan/test", methods=["GET"])
def test_plan():
    """
    Test endpoint with sample data
    Useful for quick testing via browser
    """
    sample_subjects = [
        {
            "name": "Mathematics",
            "exam_date": "2024-12-20",
            "difficulty": "hard",
            "topics": ["Calculus", "Linear Algebra", "Probability"]
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
            "topics": ["Organic Chemistry", "Inorganic Chemistry"]
        }
    ]
    
    sample_time_slots = [
        {"start": "06:00", "end": "08:00", "label": "Early Morning"},
        {"start": "09:00", "end": "11:00", "label": "Morning"},
        {"start": "14:00", "end": "16:00", "label": "Afternoon"},
        {"start": "17:00", "end": "19:00", "label": "Evening"}
    ]
    
    plan = generate_daily_plan(
        subjects=sample_subjects,
        daily_hours=6.0,
        free_time_slots=sample_time_slots
    )
    
    return jsonify({
        "success": True,
        "message": "Sample daily plan generated",
        "plan": plan
    }), 200


@app.route("/api/plan/today", methods=["GET"])
def get_today_plan_endpoint():
    """
    Get today's study plan from database
    
    Query params:
        student_id (optional): Student identifier (default: 'default')
    """
    try:
        student_id = request.args.get("student_id", "default")
        tasks = get_today_plan(student_id)
        
        if not tasks:
            return jsonify({
                "success": True,
                "message": "No plan found for today. Generate a plan first!",
                "today_plan": []
            }), 200
        
        return jsonify({
            "success": True,
            "today_plan": tasks,
            "total_tasks": len(tasks),
            "completed_tasks": sum(1 for task in tasks if task["completed"])
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch today's plan",
            "details": str(e)
        }), 500


@app.route("/api/task/complete/<int:task_id>", methods=["POST"])
def complete_task_endpoint(task_id):
    """
    Mark a task as completed
    
    Query params:
        student_id (optional): Student identifier (default: 'default')
    """
    try:
        student_id = request.args.get("student_id", "default")
        success = complete_task(task_id, student_id)
        
        if not success:
            return jsonify({
                "error": "Task not found"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Task marked as completed!",
            "task_id": task_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to complete task",
            "details": str(e)
        }), 500


@app.route("/api/streak", methods=["GET"])
def get_streak_endpoint():
    """
    Get current study streak
    
    Query params:
        student_id (optional): Student identifier (default: 'default')
    """
    try:
        student_id = request.args.get("student_id", "default")
        streak_data = get_streak(student_id)
        
        return jsonify({
            "success": True,
            "streak": streak_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch streak",
            "details": str(e)
        }), 500


@app.route("/api/progress", methods=["GET"])
def get_progress_endpoint():
    """
    Get daily progress statistics
    
    Query params:
        student_id (optional): Student identifier (default: 'default')
        date (optional): Date in YYYY-MM-DD format (default: today)
    """
    try:
        student_id = request.args.get("student_id", "default")
        progress_date = request.args.get("date")
        
        progress = get_daily_progress(student_id, progress_date)
        
        return jsonify({
            "success": True,
            "progress": progress
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch progress",
            "details": str(e)
        }), 500




# Helper for context
def get_student_context(student_id):
    """Fetch streak and progress for AI context"""
    streak = get_streak(student_id)
    progress = get_daily_progress(student_id)
    student_profile = get_student(student_id)
    name = student_profile["name"] if student_profile else None
    
    return {"streak": streak, "progress": progress, "name": name}


@app.route("/api/student/profile", methods=["POST"])
def create_profile_endpoint():
    """Create or update student profile"""
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Missing 'name'"}), 400
            
        student_id = data.get("student_id", "default")
        name = data["name"]
        
        success = create_student(student_id, name)
        
        if success:
            return jsonify({
                "success": True, 
                "message": f"Profile updated for {name}"
            }), 200
        else:
            return jsonify({"error": "Failed to create profile"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/student/profile", methods=["GET"])
def get_profile_endpoint():
    """Get student profile"""
    try:
        student_id = request.args.get("student_id", "default")
        profile = get_student(student_id)
        
        if profile:
            return jsonify({"success": True, "profile": profile}), 200
        else:
            return jsonify({"success": False, "message": "Profile not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/explain-plan", methods=["POST"])
def explain_plan_endpoint():
    """
    Generate AI explanation for a plan
    
    Expected JSON body:
    {
        "plan": { ... plan object ... },
        "mode": "english" | "hinglish" (optional)
    }
    """
    try:
        data = request.get_json()
        if not data or "plan" not in data:
            return jsonify({"error": "Missing 'plan' in body"}), 400
            
        plan = data["plan"]
        mode = data.get("mode", "english")
        
        explanation = generate_plan_explanation(plan, mode)
        
        return jsonify({
            "success": True,
            "explanation": explanation,
            "mode": mode
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/motivation", methods=["POST"])
def motivation_endpoint():
    """
    Get motivational message
    
    Expected JSON body:
    {
        "student_id": "default",
        "mode": "english" | "hinglish" (optional)
    }
    """
    try:
        data = request.get_json() or {}
        student_id = data.get("student_id", "default")
        mode = data.get("mode", "english")
        
        # Fetch context from DB
        context = get_student_context(student_id)
        
        message = generate_motivation(context, mode)
        
        return jsonify({
            "success": True,
            "message": message,
            "mode": mode
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/plan-and-motivation", methods=["POST"])
def plan_and_motivation_endpoint():
    """
    Get both explanation and motivation
    """
    try:
        data = request.get_json()
        if not data or "plan" not in data:
            return jsonify({"error": "Missing 'plan' in body"}), 400
            
        plan = data["plan"]
        student_id = data.get("student_id", "default")
        mode = data.get("mode", "english")
        
        explanation = generate_plan_explanation(plan, mode)
        
        context = get_student_context(student_id)
        motivation = generate_motivation(context, mode)
        
        return jsonify({
            "success": True,
            "explanation": explanation,
            "motivation": motivation,
            "mode": mode
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/ai/solve-doubt", methods=["POST"])
def solve_doubt_endpoint():
    """
    Solve doubt endpoint
    """
    try:
        data = request.get_json()
        if not data or "doubt" not in data:
            return jsonify({"error": "Missing 'doubt' in body"}), 400
            
        doubt = data["doubt"]
        mode = data.get("mode", "english")
        
        answer = solve_doubt(doubt, mode)
        
        return jsonify({
            "success": True,
            "answer": answer,
            "mode": mode
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/plan/upload", methods=["POST"])
def upload_syllabus_endpoint():
    """Handle syllabus file upload and parsing"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        # Save temp
        fd, path = tempfile.mkstemp(suffix="_" + file.filename)
        os.close(fd)
        file.save(path)
        
        # Read
        try:
            content = read_file_content(path)
        finally:
            if os.path.exists(path):
                os.remove(path)
        
        if not content:
             return jsonify({"error": "Could not extract text from file"}), 400

        # Parse with AI
        schedule_data = generate_schedule_from_syllabus(content)
        
        return jsonify({
            "success": True,
            "extracted_data": schedule_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/tutor", methods=["POST"])
def conversational_tutor_endpoint():
    """Interactive AI Tutor endpoint"""
    try:
        data = request.get_json()
        state = data.get("state", "START")
        context = data.get("context", {})
        user_input = data.get("user_input", "")
        
        response = generate_tutor_response(state, context, user_input)
        
        return jsonify({
            "success": True,
            "response": response
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Starting Study Saathi API...")
    print("📍 Health check: http://localhost:5000/api/health")
    print("📍 Test endpoint: http://localhost:5000/api/plan/test")
    print("📍 Daily plan: POST http://localhost:5000/api/plan/daily")
    print("📍 Weekly plan: POST http://localhost:5000/api/plan/weekly")
    print("📍 Today's plan: GET http://localhost:5000/api/plan/today")
    print("📍 Complete task: POST http://localhost:5000/api/task/complete/<task_id>")
    print("📍 Get streak: GET http://localhost:5000/api/streak")
    print("📍 Get progress: GET http://localhost:5000/api/progress")
    print("📍 AI Explain: POST http://localhost:5000/api/ai/explain-plan")
    print("📍 AI Motivation: POST http://localhost:5000/api/ai/motivation")
    app.run(debug=True, host="0.0.0.0", port=5000)
