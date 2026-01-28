# 🚀 Quick Start Guide

## Step 1: Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

## Step 2: Start the Server

```bash
python app.py
```

You should see:
```
🚀 Starting Study Saathi API...
📍 Health check: http://localhost:5000/api/health
📍 Test endpoint: http://localhost:5000/api/plan/test
📍 Daily plan: POST http://localhost:5000/api/plan/daily
📍 Weekly plan: POST http://localhost:5000/api/plan/weekly
 * Running on http://0.0.0.0:5000
```

## Step 3: Test the API

### Option A: Browser Test (Easiest)
1. Open: `http://localhost:5000/api/plan/test`
2. You should see a JSON response with a sample study plan

### Option B: Postman Test
1. Open Postman
2. Create a new POST request
3. URL: `http://localhost:5000/api/plan/daily`
4. Headers: Add `Content-Type: application/json`
5. Body: Select "raw" and "JSON", then paste the content from `example_request_daily.json`
6. Click "Send"
7. You should see a personalized study plan!

### Option C: cURL Test
```bash
curl -X POST http://localhost:5000/api/plan/daily ^
  -H "Content-Type: application/json" ^
  -d @example_request_daily.json
```

(Note: Use `^` for line continuation in Windows PowerShell, or put everything on one line)

## ✅ Success!

If you see a JSON response with a `plan` object containing schedules and time slots, you're all set! 🎉

## 📝 Next Steps

- Try modifying the subjects, exam dates, and daily hours in the example JSON files
- Test the weekly plan endpoint: `POST /api/plan/weekly`
- Integrate with your frontend application
