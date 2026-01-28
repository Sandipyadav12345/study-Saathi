# JSON Format Reference - Study Saathi API

This document shows the complete JSON format for all API requests and responses.

---

## 1. Health Check Response

**Endpoint:** `GET /api/health`

```json
{
  "status": "healthy",
  "timestamp": "2026-01-16T23:22:09.911413",
  "service": "Study Saathi API"
}
```

---

## 2. Daily Plan Request

**Endpoint:** `POST /api/plan/daily`

### Request Body:
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

**Note:** `free_time_slots` and `date` are optional.

### Response:
```json
{
  "success": true,
  "message": "Daily study plan generated successfully!",
  "plan": {
    "date": "2026-01-16",
    "total_study_hours": 6.0,
    "schedule": [
      {
        "time_slot": "Morning",
        "slot_start": "06:00",
        "slot_end": "08:00",
        "activities": [
          {
            "subject": "Mathematics",
            "subject_id": "mathematics",
            "duration_hours": 2.0,
            "start_time": "06:00",
            "end_time": "08:00",
            "difficulty": "hard",
            "topics": ["Calculus"]
          }
        ]
      },
      {
        "time_slot": "Late Morning",
        "slot_start": "09:00",
        "slot_end": "11:00",
        "activities": [
          {
            "subject": "Mathematics",
            "subject_id": "mathematics",
            "duration_hours": 1.6,
            "start_time": "09:00",
            "end_time": "10:36",
            "difficulty": "hard",
            "topics": ["Calculus"]
          },
          {
            "subject": "Physics",
            "subject_id": "physics",
            "duration_hours": 0.4,
            "start_time": "10:36",
            "end_time": "11:00",
            "difficulty": "medium",
            "topics": []
          }
        ]
      },
      {
        "time_slot": "Afternoon",
        "slot_start": "14:00",
        "slot_end": "16:00",
        "activities": [
          {
            "subject": "Physics",
            "subject_id": "physics",
            "duration_hours": 2.0,
            "start_time": "14:00",
            "end_time": "16:00",
            "difficulty": "medium",
            "topics": []
          }
        ]
      }
    ],
    "summary": {
      "subjects_count": 2,
      "time_slots_used": 3,
      "unallocated_subjects": 0
    },
    "subject_priorities": [
      {
        "subject": "Mathematics",
        "priority": 45.0,
        "difficulty": "hard",
        "days_until_exam": 1
      },
      {
        "subject": "Physics",
        "priority": 30.0,
        "difficulty": "medium",
        "days_until_exam": 1
      }
    ]
  }
}
```

---

## 3. Weekly Plan Request

**Endpoint:** `POST /api/plan/weekly`

### Request Body:
```json
{
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
  "free_time_slots": [
    {"start": "09:00", "end": "11:00", "label": "Morning"}
  ],
  "start_date": "2024-12-01"
}
```

### Response:
```json
{
  "success": true,
  "message": "Weekly study plan generated successfully!",
  "plan": {
    "week_start": "2024-12-01",
    "week_end": "2024-12-07",
    "daily_hours": 6.0,
    "days": [
      {
        "date": "2024-12-01",
        "total_study_hours": 6.0,
        "schedule": [
          {
            "time_slot": "Morning",
            "slot_start": "06:00",
            "slot_end": "08:00",
            "activities": [
              {
                "subject": "Data Structures",
                "subject_id": "data_structures",
                "duration_hours": 2.0,
                "start_time": "06:00",
                "end_time": "08:00",
                "difficulty": "hard",
                "topics": []
              }
            ]
          }
        ],
        "summary": {
          "subjects_count": 2,
          "time_slots_used": 3,
          "unallocated_subjects": 0
        },
        "subject_priorities": [
          {
            "subject": "Data Structures",
            "priority": 45.0,
            "difficulty": "hard",
            "days_until_exam": 1
          }
        ]
      }
      // ... 6 more days (2024-12-02 to 2024-12-07)
    ],
    "summary": {
      "total_subjects": 2,
      "total_study_hours_week": 42.0
    }
  }
}
```

---

## 4. Error Response

When validation fails or an error occurs:

```json
{
  "error": "Missing 'subjects' field"
}
```

Or:

```json
{
  "error": "Failed to generate plan",
  "details": "Error message here"
}
```

---

## 5. Test Endpoint Response

**Endpoint:** `GET /api/plan/test`

```json
{
  "success": true,
  "message": "Sample daily plan generated",
  "plan": {
    "date": "2026-01-16",
    "total_study_hours": 6.0,
    "schedule": [
      {
        "time_slot": "Early Morning",
        "slot_start": "06:00",
        "slot_end": "08:00",
        "activities": [
          {
            "subject": "Mathematics",
            "subject_id": "mathematics",
            "duration_hours": 2.0,
            "start_time": "06:00",
            "end_time": "08:00",
            "difficulty": "hard",
            "topics": ["Calculus", "Linear Algebra", "Probability"]
          }
        ]
      }
      // ... more time slots
    ],
    "summary": {
      "subjects_count": 3,
      "time_slots_used": 3,
      "unallocated_subjects": 0
    },
    "subject_priorities": [
      {
        "subject": "Mathematics",
        "priority": 45.0,
        "difficulty": "hard",
        "days_until_exam": 1
      }
      // ... more subjects
    ]
  }
}
```

---

## Field Descriptions

### Request Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subjects` | Array | Yes | List of subjects to study |
| `subjects[].name` | String | Yes | Subject name |
| `subjects[].exam_date` | String | Yes | Exam date (YYYY-MM-DD) |
| `subjects[].difficulty` | String | No | "easy", "medium", or "hard" (default: "medium") |
| `subjects[].topics` | Array | No | List of topics to study |
| `daily_hours` | Number | Yes | Hours available per day (0-24) |
| `free_time_slots` | Array | No | Custom time slots (uses defaults if not provided) |
| `free_time_slots[].start` | String | No | Start time (HH:MM) |
| `free_time_slots[].end` | String | No | End time (HH:MM) |
| `free_time_slots[].label` | String | No | Label for the time slot |
| `date` | String | No | Date for daily plan (default: today) |
| `start_date` | String | No | Start date for weekly plan (default: today) |

### Response Fields:

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Whether the request was successful |
| `message` | String | Success/error message |
| `plan` | Object | The generated study plan |
| `plan.date` | String | Date of the plan |
| `plan.total_study_hours` | Number | Total hours allocated |
| `plan.schedule` | Array | Time slots with activities |
| `plan.schedule[].time_slot` | String | Label of the time slot |
| `plan.schedule[].slot_start` | String | Start time of slot |
| `plan.schedule[].slot_end` | String | End time of slot |
| `plan.schedule[].activities` | Array | Study activities in this slot |
| `plan.schedule[].activities[].subject` | String | Subject name |
| `plan.schedule[].activities[].subject_id` | String | Unique subject identifier |
| `plan.schedule[].activities[].duration_hours` | Number | Hours allocated |
| `plan.schedule[].activities[].start_time` | String | Activity start time |
| `plan.schedule[].activities[].end_time` | String | Activity end time |
| `plan.schedule[].activities[].difficulty` | String | Subject difficulty |
| `plan.schedule[].activities[].topics` | Array | Topics to study |
| `plan.summary` | Object | Summary statistics |
| `plan.subject_priorities` | Array | Priority scores for each subject |

---

## Example Usage

### Using cURL:
```bash
curl -X POST http://localhost:5000/api/plan/daily \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": [
      {"name": "Math", "exam_date": "2024-12-20", "difficulty": "hard"}
    ],
    "daily_hours": 6.0
  }'
```

### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:5000/api/plan/daily",
    json={
        "subjects": [
            {"name": "Math", "exam_date": "2024-12-20", "difficulty": "hard"}
        ],
        "daily_hours": 6.0
    }
)

print(response.json())
```

### Using JavaScript (Fetch):
```javascript
fetch('http://localhost:5000/api/plan/daily', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    subjects: [
      {name: "Math", exam_date: "2024-12-20", difficulty: "hard"}
    ],
    daily_hours: 6.0
  })
})
.then(response => response.json())
.then(data => console.log(data));
```
