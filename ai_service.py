"""
AI Service Layer for Study Saathi
Handles interactions with LLM for plan explanations, motivation, and parsing.
"""
import os
import requests
import json
from typing import Dict, Any, Optional

# Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Prompts
SYSTEM_PROMPT_ENGLISH = """You are Study Saathi, a helpful AI study assistant. 
Your goal is to explain study plans clearly and provide encouraging motivation.
Keep responses concise, practical, and student-focused."""

SYSTEM_PROMPT_HINGLISH = """You are Study Saathi, a friendly Indian AI study companion. 
Speak in Hinglish (Hindi written in English script).
Use a warm, encouraging 'bhai/dost' tone.
Avoid formal corporate language. Use words like 'tension mat lo', 'aram se ho jayega', 'focus karo'.
Keep it short and punchy."""

def _call_llm(system_prompt: str, user_prompt: str) -> Optional[str]:
    """
    Internal helper to call the LLM API.
    
    Args:
        system_prompt: The system instruction setting the persona
        user_prompt: The actual content/query
        
    Returns:
        The generated text, or None if the call fails
    """
    if not LLM_API_KEY or LLM_API_KEY == "your_api_key_here":
        print("[AI SERVICE] No valid API key found. Using Mock Response.")
        return _get_mock_response(system_prompt, user_prompt)
        
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
            
    except Exception as e:
        print(f"[AI SERVICE] Error calling LLM: {str(e)}")
        
    return None

def _get_mock_response(system_prompt: str, user_prompt: str) -> str:
    """
    Returns a deterministic mock response based on the prompt type.
    Used for DEMO purposes when no API key is set.
    """
    # 1. Motivation
    if "motivational message" in user_prompt:
        if "Hinglish" in system_prompt:
        	return "Arre bhai! Tension mat lo. Bas shuru karo, sab easy hai. (Demo Mode)"
        return "Believe in yourself! Every small step counts. You got this! (Demo Mode)"

    # 2. Plan Explanation
    if "Explain this study plan" in user_prompt:
        if "Hinglish" in system_prompt:
            return "Plan mast hai! Subah fresh mind se tough subjects padho. Beech mein breaks zaroor lena. (Demo Mode)"
        return "This plan focuses on balancing difficult subjects with breaks. Review the schedule and stick to the timings. (Demo Mode)"
        
    # 3. Doubt Solving
    if "Student Doubt:" in user_prompt:
        if "Hinglish" in system_prompt:
            return "Yeh accha sawal hai! Iska basic concept samjho pehle. (Demo Answer: Set API Key for real AI)"
        return "That's a great question! Let's break it down step by step. (Demo Answer: Set API Key for real AI)"
        
    # 4. Syllabus Parsing
    if "Parse this syllabus" in user_prompt:
        # Return a valid JSON structure for the frontend to render
        return '''
        {
            "subjects": [
                {
                    "name": "Demo Mathematics",
                    "exam_date": "2026-05-01",
                    "difficulty": "hard",
                    "topics": ["Calculus", "Algebra", "Demo Topic"]
                },
                 {
                    "name": "Demo Physics",
                    "exam_date": "2026-05-05",
                    "difficulty": "medium",
                    "topics": ["Kinematics", "Dynamics"]
                }
            ]
        }
        '''
        
    # 5. Tutor Chat
    if "Student's latest response" in user_prompt or "The student wants to start" in user_prompt:
        return "That is interesting! Tell me more about it. (Demo Tutor)"
        
    return "I am in Demo Mode because no API Key was found. Please configure the .env file."

def _local_fallback_syllabus(text: str) -> Dict[str, Any]:
    """Fallback: Regex-based syllabus parsing"""
    import re
    subjects = []
    
    # Common subject names to look for
    common_subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "English", "History", "Geography", "Economics", "Accounts", "Business"]
    
    # Simple line-based extraction
    lines = text.split('\n')
    current_subject = None
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check if line looks like a subject header
        for subj in common_subjects:
            if subj.lower() in line.lower() and len(line) < 50:
                current_subject = {
                    "name": subj,
                    "exam_date": "2026-06-01", # Default
                    "difficulty": "medium",
                    "topics": []
                }
                subjects.append(current_subject)
                break
        
        # If we have a subject, treat other lines as topics
        if current_subject and line and line != current_subject["name"]:
            if len(current_subject["topics"]) < 5: # Limit topics
                current_subject["topics"].append(line[:50])
                
    if not subjects:
        # If nothing found, return a generic list based on found words
        found_words = set(text.split())
        for subj in common_subjects:
            if subj in found_words or subj.lower() in text.lower():
                subjects.append({
                    "name": subj,
                    "exam_date": "2026-06-01",
                    "difficulty": "medium",
                    "topics": ["Section A"]
                })
    
    if not subjects:
        # Absolute fallback
        subjects.append({
             "name": "General Study",
             "exam_date": "2026-06-01",
             "difficulty": "medium",
             "topics": ["Review Notes", "Practice Problems"]
        })
                
    return {"subjects": subjects}

def generate_plan_explanation(plan: Dict[str, Any], mode: str = "english") -> str:
    """
    Generate a human-friendly explanation of a study plan.
    
    Args:
        plan: The study plan JSON object
        mode: "english" or "hinglish"
    """
    # Create a concise summary of the plan for the prompt
    is_weekly = "week_start" in plan
    
    if is_weekly:
        summary = f"Weekly Plan ({plan.get('week_start')} to {plan.get('week_end')}). "
        summary += f"Total Subjects: {plan.get('summary', {}).get('total_subjects')}. "
        summary += f"Daily Hours: {plan.get('daily_hours')}."
    else:
        summary = f"Daily Plan for {plan.get('date')}. "
        summary += f"Total Hours: {plan.get('total_study_hours')}. "
        
        # Add schedule highlights
        schedule = plan.get("schedule", [])
        if schedule:
            summary += "Schedule: "
            for slot in schedule:
                summary += f"[{slot.get('time_slot')}: "
                activities = slot.get('activities', [])
                for act in activities:
                    summary += f"{act.get('subject')} ({act.get('difficulty')}), "
                summary = summary.rstrip(", ") + "]. "
    
    user_prompt = f"""
    Explain this study plan to the student in 3-4 simple sentences. 
    Highlight the key focus areas and when they need to study.
    End with 1 SHORT sentence on how this subject is used in real life (e.g. "Calculus is used in AI models").
    
    Plan Summary:
    {summary}
    """
    
    system_prompt = SYSTEM_PROMPT_HINGLISH if mode == "hinglish" else SYSTEM_PROMPT_ENGLISH
    
    response = _call_llm(system_prompt, user_prompt)
    
    # Fallbacks if AI fails
    if not response:
        if mode == "hinglish":
            return "Plan ready hai bhai! Schedule dekho aur lag jao kaam pe. All the best!"
        else:
            return "Here is your study plan. Check the schedule details above and do your best!"
            
    return response

def generate_motivation(context: Dict[str, Any], mode: str = "english") -> str:
    """
    Generate a motivational message based on student context.
    
    Args:
        context: Dictionary containing streak, progress etc.
        mode: "english" or "hinglish"
    """
    streak = context.get("streak", {}).get("current_streak", 0)
    completed_today = context.get("progress", {}).get("completed_tasks", 0)
    total_today = context.get("progress", {}).get("total_tasks", 0)
    student_name = context.get("name")
    doubt_solved = context.get("doubt_solved", False)
    
    user_prompt = f"""
    Give a short, punchy motivational message (2 sentences max).
    Focus on EFFORT and ACTION, not intelligence.
    """
    
    if student_name:
        user_prompt += f"\nAddress the student as '{student_name}'."
    
    user_prompt += f"""
    Student Context:
    - Current Streak: {streak} days
    - Today's Progress: {completed_today}/{total_today} tasks done
    - Solved a Doubt Today: {doubt_solved}
    """
    
    if doubt_solved:
         user_prompt += "They just cleared a doubt. Praise their curiosity and effort to learn!"
    elif streak > 3:
        user_prompt += "They are on a roll! Encourage them to keep consistency."
    elif total_today > 0 and completed_today == 0:
        user_prompt += "They haven't started today yet. Gently push them to take the first step."
    
    system_prompt = SYSTEM_PROMPT_HINGLISH if mode == "hinglish" else SYSTEM_PROMPT_ENGLISH
    
    response = _call_llm(system_prompt, user_prompt)
    
    # Fallbacks
    if not response:
        greeting = f"Arre {student_name} भाई," if (mode == "hinglish" and student_name) else ""
        if mode == "hinglish":
            return f"{greeting} Bas shuru kar do, sab ho jayega! Consistency is key."
        else:
            greeting = f"Hey {student_name}, " if student_name else ""
            return f"{greeting}You've got this! Just take it one step at a time."
            
    return response

def solve_doubt(doubt: str, mode: str = "english") -> str:
    """
    Solve a student doubt using Soft Socratic method.
    """
    # Soft Socratic Prompt
    socratic_system = """You are a patient, friendly tutor.
    Methodology: "Soft Socratic". 
    1. Acknowledge the question.
    2. Ask 1-2 guiding questions to help them think.
    3. Then, provide a clear, concise explanation.
    4. End with ONE short sentence on real-life usage (e.g. "Used in Rockets/Banking").
    Avoid long lectures. Keep it conversational."""
    
    socratic_system_hinglish = """You are a friendly Indian tutor (Bhai/Dost).
    Methodology: "Soft Socratic".
    1. Pehle doubt acknowledge karo.
    2. Phir 1-2 guiding questions pucho taaki wo khud soche.
    3. End mein simple explanation do.
    Use Hinglish. Be encouraging."""

    system_prompt = socratic_system_hinglish if mode == "hinglish" else socratic_system
    
    user_prompt = f"Student Doubt: {doubt}"
    
    response = _call_llm(system_prompt, user_prompt)
    
    # Fallback
    if not response:
        if mode == "hinglish":
            return "Hmm, achha sawal hai. Pehle ye batao, tumhe iske baare mein kya lagta hai? (Server busy, try again!)"
        else:
            return "Good question. What do you think is the first step here? (Server busy, try again!)"
            
    return response

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("[AI SERVICE] Failed to parse LLM JSON response")
        return _local_fallback_syllabus(syllabus_text)

def generate_schedule_from_syllabus(syllabus_text: str) -> Dict[str, Any]:
    """
    Parse raw syllabus text into a structured JSON list of subjects.
    
    Returns:
        { "subjects": [ ... ] }
    """
    if not LLM_API_KEY:
        print("[AI SERVICE] No API Key. Using fallback parsing.")
        return _local_fallback_syllabus(syllabus_text)

    system_prompt = """You are a Syllabus Parsing Assistant. 
    Extract subjects, topics, and estimated difficulty from the provided syllabus text.
    Return ONLY valid JSON in the following format:
    {
        "subjects": [
            {
                "name": "Subject Name",
                "exam_date": "YYYY-MM-DD" (estimate 1 month from now if not found),
                "difficulty": "medium" (infer from content complexity),
                "topics": ["Topic 1", "Topic 2", ...]
            }
        ]
    }
    """
    
    user_prompt = f"""
    Parse this syllabus and extract the structured data:
    
    SIDENOTE: If you cannot find an exam date, assume it is 30 days from today ({os.getenv('CURRENT_DATE', '2024-12-01')}).
    
    Syllabus Text:
    {syllabus_text[:2000]}  # Limit text length for token limits
    """
    
    response = _call_llm(system_prompt, user_prompt)
    
    if not response:
        return _local_fallback_syllabus(syllabus_text)
        
    # Clean up JSON if LLM adds markdown
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0].strip()
    elif "```" in response:
        response = response.split("```")[1].split("```")[0].strip()
        
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("[AI SERVICE] Failed to parse LLM JSON response")
        return _local_fallback_syllabus(syllabus_text)

def generate_tutor_response(state: str, context: Dict[str, Any], user_input: str) -> Dict[str, str]:
    """
    Generate the next response in the interactive tutor flow.
    """
    system_prompt = """You are a wise and friendly personal tutor (Study Saathi).
    Your goal is to guide the student interactively.
    Always keep responses short (maximum 2-3 sentences).
    Use a warm, conversational tone.
    """
    
    # Construct the appropriate prompt based on state
    if state == "START":
        user_prompt = "The student wants to start studying. Ask them enthusiastically: 'Which subject would you like to study today?'"
    
    elif state == "SUBJECT_SELECTED":
        subject = context.get("subject", "this subject")
        user_prompt = f"The student chose '{subject}'. Ask them specifically which TOPIC within {subject} they want to focus on."
    
    elif state == "TOPIC_SELECTED":
        topic = context.get("topic", "this topic")
        user_prompt = f"The student chose topic '{topic}'. Ask them kindly: 'What do you already know about {topic}?' to gauge their level."
        
    elif state == "TEACHING":
        topic = context.get("topic", "the topic")
        
        user_prompt = f"""
        Topic: {topic}
        Student's latest response: "{user_input}"
        
        Task:
        1. Acknowledge their answer (correct/incorrect/partial).
        2. Use the Socratic method: Explain a bit, then ASK a follow-up question to check understanding.
        3. Do NOT lecture. Keep it interactive.
        """
        
    else:
        user_prompt = f"Respond to: {user_input}"

    response_text = _call_llm(system_prompt, user_prompt)
    
    if not response_text:
        # Simple fallback conversation
        if state == "START":
             return {"text": "Hello! I am your Study Saathi. Which subject are we studying?", "state": "SUBJECT_SELECTED"}
        elif state == "SUBJECT_SELECTED":
             return {"text": "Great choice! What topic specifically?", "state": "TOPIC_SELECTED"}
        elif state == "TOPIC_SELECTED":
             return {"text": "Okay, let's dive in. What is the first thing that comes to mind when you think of this?", "state": "TEACHING"}
        else:
             return {"text": "That's interesting! Tell me more.", "state": state}
        
    return {"text": response_text, "state": state}
