"""
Database module for Study Saathi
Handles SQLite database operations for study plans, tasks, and streaks
"""
import sqlite3
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

DB_NAME = "study_saathi.db"


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_db():
    """Initialize database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Study Plans Table - stores generated study plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            plan_date TEXT NOT NULL,
            plan_type TEXT NOT NULL,  -- 'daily' or 'weekly'
            total_hours REAL,
            subjects_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, plan_date, plan_type)
        )
    """)

    # Study Tasks Table - individual tasks from plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            subject TEXT NOT NULL,
            subject_id TEXT,
            study_hours REAL NOT NULL,
            start_time TEXT,
            end_time TEXT,
            time_slot TEXT,
            difficulty TEXT,
            topics TEXT,  -- JSON string of topics array
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            FOREIGN KEY (plan_id) REFERENCES study_plans(id) ON DELETE CASCADE
        )
    """)

    # Streak Table - tracks study streaks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            student_id TEXT PRIMARY KEY DEFAULT 'default',
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_study_date TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # Daily Progress Table - tracks daily completion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            progress_date TEXT NOT NULL,
            total_tasks INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            total_hours REAL DEFAULT 0,
            completed_hours REAL DEFAULT 0,
            UNIQUE(student_id, progress_date)
        )
    """)

    # Students Table - stores simple profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DATABASE] Initialized database: {DB_NAME}")


def save_study_plan(plan_data: Dict[str, Any], plan_type: str = "daily", student_id: str = "default") -> int:
    """
    Save a study plan to database
    
    Args:
        plan_data: The plan data from generate_daily_plan or generate_weekly_plan
        plan_type: 'daily' or 'weekly'
        student_id: Student identifier (default: 'default')
    
    Returns:
        plan_id: The ID of the saved plan
    """
    conn = get_connection()
    cursor = conn.cursor()

    plan_date = plan_data.get("date") or plan_data.get("week_start", str(date.today()))
    total_hours = plan_data.get("total_study_hours", 0)
    subjects_count = plan_data.get("summary", {}).get("subjects_count", 0)

    # Insert or update study plan
    cursor.execute("""
        INSERT OR REPLACE INTO study_plans 
        (student_id, plan_date, plan_type, total_hours, subjects_count)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, plan_date, plan_type, total_hours, subjects_count))

    plan_id = cursor.lastrowid

    # For daily plans, save tasks from schedule
    if plan_type == "daily" and "schedule" in plan_data:
        # Delete old tasks for this plan
        cursor.execute("DELETE FROM study_tasks WHERE plan_id=?", (plan_id,))
        
        for slot in plan_data["schedule"]:
            for activity in slot.get("activities", []):
                topics_json = str(activity.get("topics", []))
                cursor.execute("""
                    INSERT INTO study_tasks 
                    (plan_id, subject, subject_id, study_hours, start_time, end_time, 
                     time_slot, difficulty, topics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    plan_id,
                    activity.get("subject"),
                    activity.get("subject_id"),
                    activity.get("duration_hours", 0),
                    activity.get("start_time"),
                    activity.get("end_time"),
                    slot.get("time_slot"),
                    activity.get("difficulty"),
                    topics_json
                ))

    # For weekly plans, save tasks from each day
    elif plan_type == "weekly" and "days" in plan_data:
        cursor.execute("DELETE FROM study_tasks WHERE plan_id=?", (plan_id,))
        
        for day_plan in plan_data["days"]:
            day_date = day_plan.get("date")
            for slot in day_plan.get("schedule", []):
                for activity in slot.get("activities", []):
                    topics_json = str(activity.get("topics", []))
                    cursor.execute("""
                        INSERT INTO study_tasks 
                        (plan_id, subject, subject_id, study_hours, start_time, end_time, 
                         time_slot, difficulty, topics)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        plan_id,
                        activity.get("subject"),
                        activity.get("subject_id"),
                        activity.get("duration_hours", 0),
                        activity.get("start_time"),
                        activity.get("end_time"),
                        slot.get("time_slot"),
                        activity.get("difficulty"),
                        topics_json
                    ))

    conn.commit()
    conn.close()
    return plan_id


def get_today_plan(student_id: str = "default") -> List[Dict[str, Any]]:
    """
    Get today's study plan from database
    
    Returns:
        List of tasks for today
    """
    conn = get_connection()
    cursor = conn.cursor()

    today = str(date.today())

    # Get today's plan
    cursor.execute("""
        SELECT id FROM study_plans 
        WHERE student_id=? AND plan_date=? AND plan_type='daily'
        ORDER BY created_at DESC LIMIT 1
    """, (student_id, today))

    plan_row = cursor.fetchone()

    if not plan_row:
        conn.close()
        return []

    plan_id = plan_row["id"]

    # Get all tasks for this plan
    cursor.execute("""
        SELECT id, subject, subject_id, study_hours, start_time, end_time,
               time_slot, difficulty, topics, completed, completed_at
        FROM study_tasks
        WHERE plan_id=?
        ORDER BY start_time ASC
    """, (plan_id,))

    tasks = []
    for row in cursor.fetchall():
        # Parse topics from string
        topics = []
        if row["topics"]:
            try:
                import ast
                topics = ast.literal_eval(row["topics"])
            except:
                topics = []

        tasks.append({
            "task_id": row["id"],
            "subject": row["subject"],
            "subject_id": row["subject_id"],
            "study_hours": row["study_hours"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "time_slot": row["time_slot"],
            "difficulty": row["difficulty"],
            "topics": topics,
            "completed": bool(row["completed"]),
            "completed_at": row["completed_at"]
        })

    conn.close()
    return tasks


def complete_task(task_id: int, student_id: str = "default") -> bool:
    """
    Mark a task as completed
    
    Returns:
        True if task was found and updated
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if task exists
    cursor.execute("SELECT id, completed FROM study_tasks WHERE id=?", (task_id,))
    task = cursor.fetchone()

    if not task:
        conn.close()
        return False

    # Update task
    cursor.execute("""
        UPDATE study_tasks 
        SET completed=1, completed_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (task_id,))

    # Update daily progress
    today = str(date.today())
    cursor.execute("""
        INSERT OR IGNORE INTO daily_progress 
        (student_id, progress_date, total_tasks, completed_tasks, total_hours, completed_hours)
        SELECT 
            ?,
            ?,
            COUNT(*),
            0,
            SUM(study_hours),
            0
        FROM study_tasks
        WHERE plan_id IN (
            SELECT id FROM study_plans 
            WHERE student_id=? AND plan_date=? AND plan_type='daily'
        )
    """, (student_id, today, student_id, today))

    # Update completed tasks and hours
    cursor.execute("""
        UPDATE daily_progress
        SET 
            completed_tasks = (
                SELECT COUNT(*) FROM study_tasks
                WHERE plan_id IN (
                    SELECT id FROM study_plans 
                    WHERE student_id=? AND plan_date=? AND plan_type='daily'
                ) AND completed=1
            ),
            completed_hours = (
                SELECT COALESCE(SUM(study_hours), 0) FROM study_tasks
                WHERE plan_id IN (
                    SELECT id FROM study_plans 
                    WHERE student_id=? AND plan_date=? AND plan_type='daily'
                ) AND completed=1
            )
        WHERE student_id=? AND progress_date=?
    """, (student_id, today, student_id, today, student_id, today))

    conn.commit()
    conn.close()

    # Update streak after task completion
    update_streak(student_id)

    return True


def update_streak(student_id: str = "default"):
    """
    Update study streak based on today's progress
    """
    conn = get_connection()
    cursor = conn.cursor()

    today = str(date.today())

    # Get current streak
    cursor.execute("""
        SELECT current_streak, longest_streak, last_study_date 
        FROM streaks 
        WHERE student_id=?
    """, (student_id,))

    row = cursor.fetchone()

    # Check if there's progress today
    cursor.execute("""
        SELECT completed_tasks FROM daily_progress
        WHERE student_id=? AND progress_date=?
    """, (student_id, today))

    progress = cursor.fetchone()
    has_progress = progress and progress["completed_tasks"] > 0

    if not row:
        # First time - create streak
        if has_progress:
            cursor.execute("""
                INSERT INTO streaks (student_id, current_streak, longest_streak, last_study_date)
                VALUES (?, 1, 1, ?)
            """, (student_id, today))
    else:
        last_study_date = row["last_study_date"]
        current_streak = row["current_streak"]
        longest_streak = row["longest_streak"]

        if has_progress:
            if last_study_date == today:
                # Already updated today, don't increment
                pass
            elif last_study_date == str(date.today() - timedelta(days=1)):
                # Consecutive day - increment streak
                new_streak = current_streak + 1
                new_longest = max(new_streak, longest_streak)
                cursor.execute("""
                    UPDATE streaks 
                    SET current_streak=?, longest_streak=?, last_study_date=?, updated_at=CURRENT_TIMESTAMP
                    WHERE student_id=?
                """, (new_streak, new_longest, today, student_id))
            else:
                # Streak broken - reset to 1
                cursor.execute("""
                    UPDATE streaks 
                    SET current_streak=1, last_study_date=?, updated_at=CURRENT_TIMESTAMP
                    WHERE student_id=?
                """, (today, student_id))
        # If no progress today, don't update (streak continues until broken)

    conn.commit()
    conn.close()


def get_streak(student_id: str = "default") -> Dict[str, Any]:
    """
    Get current streak information
    
    Returns:
        Dictionary with streak data
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT current_streak, longest_streak, last_study_date
        FROM streaks
        WHERE student_id=?
    """, (student_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_study_date": None
        }

    return {
        "current_streak": row["current_streak"],
        "longest_streak": row["longest_streak"],
        "last_study_date": row["last_study_date"]
    }


def get_daily_progress(student_id: str = "default", progress_date: str = None) -> Dict[str, Any]:
    """
    Get daily progress statistics
    
    Args:
        student_id: Student identifier
        progress_date: Date in YYYY-MM-DD format (default: today)
    
    Returns:
        Progress statistics
    """
    if progress_date is None:
        progress_date = str(date.today())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total_tasks, completed_tasks, total_hours, completed_hours
        FROM daily_progress
        WHERE student_id=? AND progress_date=?
    """, (student_id, progress_date))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "date": progress_date,
            "total_tasks": 0,
            "completed_tasks": 0,
            "total_hours": 0.0,
            "completed_hours": 0.0,
            "completion_percentage": 0.0
        }

    total_tasks = row["total_tasks"] or 0
    completed_tasks = row["completed_tasks"] or 0
    total_hours = row["total_hours"] or 0.0
    completed_hours = row["completed_hours"] or 0.0

    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0


    return {
        "date": progress_date,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_hours": round(total_hours, 2),
        "completed_hours": round(completed_hours, 2),
        "completion_percentage": round(completion_percentage, 2)
    }


def create_student(student_id: str, name: str) -> bool:
    """
    Create or update a student profile
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO students (id, name)
            VALUES (?, ?)
        """, (student_id, name))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating student: {e}")
        return False
    finally:
        conn.close()


def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Get student profile
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, created_at FROM students WHERE id=?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"]
    }
