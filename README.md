# Study Saathi - Backend API

AI-powered study planner for Indian college students.

## 🚀 Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running.

**Example:**
```bash
curl http://localhost:5000/api/health
```

Or open in browser: `http://localhost:5000/api/health`

---

### 2. Test Endpoint (Sample Data)
**GET** `/api/plan/test`

Generate a sample daily study plan with test data. Perfect for quick testing!

**Example:**
- Browser: `http://localhost:5000/api/plan/test`
- cURL: `curl http://localhost:5000/api/plan/test`

---

### 3. Generate Daily Plan
**POST** `/api/plan/daily`

Generate a personalized daily study plan.

**Request Body:**
```json
{
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
    }
  ],
  "daily_hours": 6.0,
  "free_time_slots": [
    {"start": "09:00", "end": "11:00", "label": "Morning"},
    {"start": "14:00", "end": "16:00", "label": "Afternoon"},
    {"start": "17:00", "end": "19:00", "label": "Evening"}
  ],
  "date": "2024-12-01"
}
```

**Fields:**
- `subjects` (required): Array of subject objects
  - `name` (required): Subject name
  - `exam_date` (required): Exam date in YYYY-MM-DD format
  - `difficulty` (optional): "easy", "medium", or "hard" (default: "medium")
  - `topics` (optional): Array of topics to study
- `daily_hours` (required): Total hours available for study per day (0-24)
- `free_time_slots` (optional): Custom time slots. If not provided, default slots are used
- `date` (optional): Date for the plan (default: today)

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/api/plan/daily \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": [
      {
        "name": "Mathematics",
        "exam_date": "2024-12-20",
        "difficulty": "hard",
        "topics": ["Calculus"]
      }
    ],
    "daily_hours": 6.0
  }'
```

**Example with Postman:**
1. Method: POST
2. URL: `http://localhost:5000/api/plan/daily`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Use the request body example above

---

### 4. Generate Weekly Plan
**POST** `/api/plan/weekly`

Generate a personalized weekly study plan (7 days).

**Request Body:**
Same as daily plan, but use `start_date` instead of `date`:
```json
{
  "subjects": [...],
  "daily_hours": 6.0,
  "free_time_slots": [...],
  "start_date": "2024-12-01"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/api/plan/weekly \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": [
      {
        "name": "Mathematics",
        "exam_date": "2024-12-20",
        "difficulty": "hard"
      }
    ],
    "daily_hours": 6.0
  }'
```

---

## 📋 Response Format

### Success Response:
```json
{
  "success": true,
  "plan": {
    "date": "2024-12-01",
    "total_study_hours": 6.0,
    "schedule": [
      {
        "time_slot": "Morning",
        "slot_start": "09:00",
        "slot_end": "11:00",
        "activities": [
          {
            "subject": "Mathematics",
            "subject_id": "mathematics",
            "duration_hours": 2.0,
            "start_time": "09:00",
            "end_time": "11:00",
            "difficulty": "hard",
            "topics": ["Calculus"]
          }
        ]
      }
    ],
    "summary": {
      "subjects_count": 2,
      "time_slots_used": 3,
      "unallocated_subjects": 0
    },
    "subject_priorities": [...]
  },
  "message": "Daily study plan generated successfully!"
}
```

### Error Response:
```json
{
  "error": "Missing 'subjects' field"
}
```

---

## 🧪 Testing

### Quick Test (Browser)
1. Start the server: `python app.py`
2. Open browser: `http://localhost:5000/api/plan/test`

### Test with Postman
1. Import the collection or create a new request
2. Use POST method for `/api/plan/daily` or `/api/plan/weekly`
3. Set Content-Type header to `application/json`
4. Add JSON body with your subjects and preferences
5. Send request and view the generated plan

### Test with cURL
See examples above in each endpoint section.

---

## 🎯 How It Works

1. **Priority Calculation**: 
   - Higher priority for harder subjects
   - Higher priority for exams closer to today
   - Extra boost if exam is within 7 days

2. **Time Allocation**:
   - Time is distributed proportionally based on priority scores
   - Subjects are scheduled into available time slots

3. **Smart Scheduling**:
   - Fits subjects into your free time slots
   - Distributes study time across the day
   - Handles multiple subjects efficiently

---

## ✨ Flexibility & Customization

**The API is NOT limited to sample subjects!** It works with **ANY subjects** you provide:

- ✅ **Any number of subjects** (1, 5, 10, or more)
- ✅ **Any subject names** (Mathematics, Physics, CS, Engineering, Commerce, Arts, etc.)
- ✅ **Any exam dates** (past, present, or future)
- ✅ **Any difficulty levels** (easy, medium, hard)
- ✅ **Any topics** (customize what to study in each subject)
- ✅ **Any daily hours** (2 hours, 6 hours, 10 hours, etc.)
- ✅ **Any time slots** (customize your free time)

### Examples of Real Use Cases:

**Engineering Student:**
```json
{
  "subjects": [
    {"name": "Data Structures", "exam_date": "2024-12-15", "difficulty": "hard"},
    {"name": "Operating Systems", "exam_date": "2024-12-18", "difficulty": "hard"},
    {"name": "DBMS", "exam_date": "2024-12-20", "difficulty": "medium"}
  ],
  "daily_hours": 8.0
}
```

**Medical Student:**
```json
{
  "subjects": [
    {"name": "Anatomy", "exam_date": "2024-12-15", "difficulty": "hard"},
    {"name": "Physiology", "exam_date": "2024-12-18", "difficulty": "medium"},
    {"name": "Biochemistry", "exam_date": "2024-12-20", "difficulty": "hard"}
  ],
  "daily_hours": 10.0
}
```

**Commerce Student:**
```json
{
  "subjects": [
    {"name": "Accountancy", "exam_date": "2024-12-15", "difficulty": "hard"},
    {"name": "Business Studies", "exam_date": "2024-12-18", "difficulty": "easy"},
    {"name": "Economics", "exam_date": "2024-12-20", "difficulty": "medium"}
  ],
  "daily_hours": 6.0
}
```

**The `/api/plan/test` endpoint is just for quick testing** - it uses sample data so you can test without sending a POST request. The real endpoints (`/api/plan/daily` and `/api/plan/weekly`) accept **your custom subjects** via POST request.

---

---

## 💾 Database Endpoints (NEW - Day 3)

### 5. Get Today's Plan
**GET** `/api/plan/today`

Retrieve today's study plan from database.

**Query Parameters:**
- `student_id` (optional): Student identifier (default: 'default')

**Example:**
```bash
curl http://localhost:5000/api/plan/today
curl http://localhost:5000/api/plan/today?student_id=user123
```

**Response:**
```json
{
  "success": true,
  "today_plan": [
    {
      "task_id": 1,
      "subject": "Mathematics",
      "subject_id": "mathematics",
      "study_hours": 2.0,
      "start_time": "09:00",
      "end_time": "11:00",
      "time_slot": "Morning",
      "difficulty": "hard",
      "topics": ["Calculus"],
      "completed": false,
      "completed_at": null
    }
  ],
  "total_tasks": 5,
  "completed_tasks": 0
}
```

---

### 6. Complete Task
**POST** `/api/task/complete/<task_id>`

Mark a study task as completed. Automatically updates streak and progress.

**Query Parameters:**
- `student_id` (optional): Student identifier (default: 'default')

**Example:**
```bash
curl -X POST http://localhost:5000/api/task/complete/1
curl -X POST http://localhost:5000/api/task/complete/1?student_id=user123
```

**Response:**
```json
{
  "success": true,
  "message": "Task marked as completed!",
  "task_id": 1
}
```

---

### 7. Get Streak
**GET** `/api/streak`

Get current study streak information.

**Query Parameters:**
- `student_id` (optional): Student identifier (default: 'default')

**Example:**
```bash
curl http://localhost:5000/api/streak
```

**Response:**
```json
{
  "success": true,
  "streak": {
    "current_streak": 5,
    "longest_streak": 10,
    "last_study_date": "2024-12-16"
  }
}
```

---

### 8. Get Progress
**GET** `/api/progress`

Get daily progress statistics.

**Query Parameters:**
- `student_id` (optional): Student identifier (default: 'default')
- `date` (optional): Date in YYYY-MM-DD format (default: today)

**Example:**
```bash
curl http://localhost:5000/api/progress
curl http://localhost:5000/api/progress?date=2024-12-15
```

**Response:**
```json
{
  "success": true,
  "progress": {
    "date": "2024-12-16",
    "total_tasks": 5,
    "completed_tasks": 3,
    "total_hours": 6.0,
    "completed_hours": 3.6,
    "completion_percentage": 60.0
  }
}
```

---

### 9. AI Explain Plan
**POST** `/api/ai/explain-plan`

Get a human-friendly explanation of the study plan.

**Request Body:**
```json
{
  "plan": { ... },     // The plan object from /api/plan/daily
  "mode": "english"    // or "hinglish"
}
```

---

### 10. AI Motivation
**POST** `/api/ai/motivation`

Get a personalized motivational message based on streak/progress.

**Request Body:**
```json
{
  "student_id": "default",
  "mode": "hinglish"   // or "english"
}
```

---

### 11. Plan + Motivation (Combined)
**POST** `/api/ai/plan-and-motivation`

Get both explanation and motivation in one call.

**Request Body:**
```json
{
  "plan": { ... },
  "student_id": "default",
  "mode": "english"
}
```

---


## 🗄️ Database

The API uses SQLite database (`study_saathi.db`) to store:
- **Study Plans**: Generated daily/weekly plans
- **Study Tasks**: Individual tasks from plans
- **Streaks**: Study streak tracking
- **Daily Progress**: Completion statistics

The database is automatically initialized when the server starts.

**Database Schema:**
- `study_plans`: Stores plan metadata
- `study_tasks`: Individual study tasks with completion status
- `streaks`: Current and longest streaks
- `daily_progress`: Daily completion statistics

---

## 🔧 Next Steps (Future Enhancements)

- [x] Store study plans in database ✅
- [x] Track study progress ✅
- [x] Basic streak logic ✅
- [ ] Add user authentication
- [ ] Send daily reminders
- [x] Multi-language support (Hindi/English) ✅
- [ ] Mobile app integration
