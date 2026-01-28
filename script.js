const API_BASE = "https://study-saathi-3tax.onrender.com/api";

// DOM Elements
const setupScreen = document.getElementById('setup-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const studentNameInput = document.getElementById('student-name');
const btnStart = document.getElementById('btn-start');
const btnLogout = document.getElementById('btn-logout');

// Plan View Elements
const btnGenerate = document.getElementById('btn-generate-plan');
const btnViewDaily = document.getElementById('btn-view-daily');
const btnViewOverall = document.getElementById('btn-view-overall');
const planSectionTitle = document.getElementById('plan-section-title');
const planContainerEl = document.getElementById('plan-container');
const explanationTextEl = document.getElementById('explanation-text');

// Syllabus Elements
const fileInput = document.getElementById('syllabus-file');
// Allow images
if (fileInput) fileInput.accept = ".pdf,.docx,.txt,.jpg,.jpeg,.png";

const dailyHoursInput = document.getElementById('user-daily-hours');
const btnProcessSyllabus = document.getElementById('btn-process-syllabus');

// Tutor Elements
const btnStartTutor = document.getElementById('btn-start-tutor');
const btnMicToggle = document.getElementById('btn-mic-toggle');
const tutorChatArea = document.getElementById('tutor-chat-area');
const tutorTextInput = document.getElementById('tutor-text-input');

// Motivation
const greetingEl = document.getElementById('greeting');
const motivationTextEl = document.getElementById('motivation-text');
const streakCountEl = document.getElementById('streak-count');
const progressPercentEl = document.getElementById('progress-percent');

// Doubt Solver
const doubtInput = document.getElementById('doubt-input');
const btnSolveDoubt = document.getElementById('btn-solve-doubt');
const doubtResponseEl = document.getElementById('doubt-response');
const doubtResponseText = document.getElementById('doubt-response-text');

// State
let currentUser = {
    name: "",
    id: "default",
    language: "english",
    doubtSolvedSession: false
};

let tutorState = {
    active: false,
    state: "START",
    context: {},
    isListening: false
};

let overallScheduleCache = null;

// Speech Setup
const synth = window.speechSynthesis;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        addChatMessage("You", transcript);
        handleTutorInteraction(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech error", event.error);
        tutorState.isListening = false;
        updateMicButton();
    };

    recognition.onend = () => {
        tutorState.isListening = false;
        updateMicButton();
    };
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    loadUser();
});

function loadUser() {
    const savedUser = localStorage.getItem('studySaathiUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showDashboard();
    } else {
        showSetup();
    }
}

function showSetup() {
    setupScreen.classList.remove('hidden');
    dashboardScreen.classList.add('hidden');
}

function showDashboard() {
    setupScreen.classList.add('hidden');
    dashboardScreen.classList.remove('hidden');
    greetingEl.textContent = `Hello, ${currentUser.name}! 👋`;

    // Sync Profile
    currentUser.id = currentUser.name.toLowerCase().replace(/\s+/g, '_') + "_v1";
    fetch(`${API_BASE}/student/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: currentUser.id, name: currentUser.name })
    }).catch(console.error);

    loadMotivation();
    loadTodayPlan();
    loadStats();
}

// --- Event Listeners ---

btnStart.addEventListener('click', () => {
    const name = studentNameInput.value.trim();
    if (!name) return alert("Please enter your name!");
    const lang = document.querySelector('input[name="language"]:checked').value;
    currentUser = { name, language: lang };
    localStorage.setItem('studySaathiUser', JSON.stringify(currentUser));
    showDashboard();
});

btnLogout.addEventListener('click', () => {
    localStorage.removeItem('studySaathiUser');
    location.reload();
});

// Plan Views
btnViewDaily.addEventListener('click', () => {
    setActiveView('daily');
    loadTodayPlan();
});

btnViewOverall.addEventListener('click', () => {
    setActiveView('overall');
    renderOverallSchedule();
});

function setActiveView(view) {
    if (view === 'daily') {
        btnViewDaily.classList.replace('btn-secondary', 'btn-primary');
        btnViewDaily.style.opacity = '1';
        btnViewOverall.classList.replace('btn-primary', 'btn-secondary');
        btnViewOverall.style.opacity = '0.6';
        planSectionTitle.textContent = "Today's Plan";
    } else {
        btnViewOverall.classList.replace('btn-secondary', 'btn-primary');
        btnViewOverall.style.opacity = '1';
        btnViewDaily.classList.replace('btn-primary', 'btn-secondary');
        btnViewDaily.style.opacity = '0.6';
        planSectionTitle.textContent = "Overall Schedule";
    }
}

// Syllabus Upload
btnProcessSyllabus.addEventListener('click', async () => {
    const dailyHours = dailyHoursInput.value;
    const file = fileInput.files[0];

    if (!file) {
        // Manual Entry: Prompt user for subjects
        const manual = prompt("No file selected. Enter subjects (comma separated):\nExample: Mathematics, Physics, Chemistry");
        if (!manual || manual.trim() === '') return;

        const subjects = manual.split(',').map(s => ({
            name: s.trim(),
            exam_date: "2026-06-01",
            difficulty: "medium",
            topics: []
        }));

        explanationTextEl.textContent = "AI naya plan bana raha hai... 🤖";
        planContainerEl.innerHTML = '<p class="loading-text">Generating smart plan...</p>';

        const payload = {
            student_id: currentUser.id,
            daily_hours: parseFloat(dailyHours),
            subjects: subjects
        };

        try {
            const res = await fetch(`${API_BASE}/plan/daily`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (data.success) {
                loadTodayPlan();
                btnViewDaily.click();
                alert("Plan Generated Successfully based on your subjects!");
            } else {
                alert("Failed: " + data.error);
            }
        } catch (err) {
            console.error(err);
            alert("Planning failed.");
        }
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('daily_hours', dailyHours);

    btnProcessSyllabus.textContent = "Processing... ⏳";
    btnProcessSyllabus.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/plan/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (data.success) {
            alert("Syllabus parsed! AI is generating your schedule...");
            // Now call generate plan with extracted subjects
            const payload = {
                student_id: currentUser.id,
                daily_hours: parseFloat(dailyHours),
                subjects: data.extracted_data.subjects
            };

            await generatePlanFromSyllabus(payload);
        } else {
            alert("Error: " + data.error);
        }
    } catch (err) {
        console.error(err);
        alert("Upload failed.");
    } finally {
        btnProcessSyllabus.textContent = "Generate Schedule 📅";
        btnProcessSyllabus.disabled = false;
    }
});

// Auto-Generate Plan (Button Listener)
btnGenerate.addEventListener('click', generateNewPlan);

async function generateNewPlan() {
    // Prompt user for subjects
    const manual = prompt("Enter subjects you want to study (comma separated):\nExample: Mathematics, Physics, Chemistry");
    if (!manual || manual.trim() === '') return;

    const subjects = manual.split(',').map(s => ({
        name: s.trim(),
        exam_date: "2026-06-01",
        difficulty: "medium",
        topics: []
    }));

    explanationTextEl.textContent = "AI naya plan bana raha hai... 🤖";
    planContainerEl.innerHTML = '<p class="loading-text">Generating smart plan...</p>';

    const payload = {
        student_id: currentUser.id,
        daily_hours: 6.0,
        subjects: subjects
    };

    try {
        const res = await fetch(`${API_BASE}/plan/daily`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            loadTodayPlan();
            btnViewDaily.click();
            alert("Plan generated based on your subjects!");
        } else {
            alert("Failed to generate plan: " + data.error);
        }
    } catch (err) {
        console.error(err);
        alert("Server error during generation");
    }
}

async function generatePlanFromSyllabus(payload) {
    try {
        // Generate DAILY plan first (this is what shows in "Today's Plan")
        const dailyRes = await fetch(`${API_BASE}/plan/daily`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const dailyData = await dailyRes.json();

        if (dailyData.success) {
            // Also generate weekly plan in background for "Overall Schedule" view
            fetch(`${API_BASE}/plan/weekly`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(r => r.json()).then(d => {
                if (d.success) overallScheduleCache = d.plan;
            });

            // Load and display today's plan
            loadTodayPlan();
            btnViewDaily.click();
            alert("Schedule Generated Successfully! Check Today's Plan.");
        } else {
            alert("Failed to generate plan: " + dailyData.error);
        }
    } catch (err) {
        console.error(err);
        alert("Planning failed.");
    }
}

// Doubt Solver Logic
btnSolveDoubt.addEventListener('click', async () => {
    const doubt = doubtInput.value.trim();
    if (!doubt) return alert("Please enter your doubt!");

    btnSolveDoubt.textContent = "Solving... 🧘";
    btnSolveDoubt.disabled = true;
    doubtResponseEl.classList.add('hidden');

    try {
        const res = await fetch(`${API_BASE}/ai/solve-doubt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doubt: doubt, mode: currentUser.language })
        });
        const data = await res.json();

        if (data.success) {
            doubtResponseText.textContent = data.answer;
            doubtResponseEl.classList.remove('hidden');
            currentUser.doubtSolvedSession = true;
            // Refresh stats to show progress if solve-doubt contributes
            loadStats();
        } else {
            alert("Error: " + data.error);
        }
    } catch (err) {
        console.error(err);
        alert("Doubt solving failed.");
    } finally {
        btnSolveDoubt.textContent = "Solve Doubt 💡";
        btnSolveDoubt.disabled = false;
    }
});

// Interactive Tutor
btnStartTutor.addEventListener('click', () => {
    tutorState.active = true;
    tutorState.state = "START";
    tutorState.context = {};
    addChatMessage("AI", "Starting session... (Say 'Math' or 'Science' to begin)");
    handleTutorInteraction(""); // Start loop
    btnMicToggle.disabled = false;
});

btnMicToggle.addEventListener('click', () => {
    if (!recognition) return alert("Voice not supported in this browser.");
    if (tutorState.isListening) {
        recognition.stop();
    } else {
        recognition.start();
        tutorState.isListening = true;
    }
    updateMicButton();
});

tutorTextInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const text = tutorTextInput.value;
        addChatMessage("You", text);
        handleTutorInteraction(text);
        tutorTextInput.value = '';
    }
});

async function handleTutorInteraction(userInput) {
    // Call Backend
    try {
        const res = await fetch(`${API_BASE}/ai/tutor`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                state: tutorState.state,
                context: tutorState.context,
                user_input: userInput
            })
        });
        const data = await res.json();

        if (data.success) {
            const aiText = data.response.text;
            tutorState.state = data.response.state;

            addChatMessage("AI", aiText);

            // Voice Fix: Ensure synth is cancelled before speaking to reset
            if (synth.speaking) synth.cancel();
            speak(aiText);

            // Infer state transitions specifically for "Start"
            if (tutorState.state === "START" && userInput) {
                tutorState.state = "SUBJECT_SELECTED";
                tutorState.context.subject = userInput;
            } else if (tutorState.state === "SUBJECT_SELECTED" && userInput) {
                tutorState.state = "TOPIC_SELECTED";
                tutorState.context.topic = userInput;
            } else if (tutorState.state === "TOPIC_SELECTED" && userInput) {
                tutorState.state = "TEACHING";
            }
        }
    } catch (err) {
        console.error(err);
        addChatMessage("System", "Tutor is currently offline.");
    }
}

function addChatMessage(sender, text) {
    const p = document.createElement('p');
    p.className = sender === "AI" ? "ai-msg" : "user-msg";
    p.textContent = `${sender}: ${text}`;
    p.style.textAlign = sender === "AI" ? "left" : "right";
    p.style.color = sender === "AI" ? "#333" : "#6c63ff";
    tutorChatArea.appendChild(p);
    tutorChatArea.scrollTop = tutorChatArea.scrollHeight;
}

function speak(text) {
    if (synth.speaking) synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    // Try to pick a voice
    const voices = synth.getVoices();
    // Prefer Indian English if available for "Study Saathi" feel
    const voice = voices.find(v => v.lang.includes('IN')) || voices[0];
    if (voice) utterance.voice = voice;
    synth.speak(utterance);
}

function updateMicButton() {
    btnMicToggle.textContent = tutorState.isListening ? "🔴 Listening..." : "🎤 Speak";
    btnMicToggle.classList.toggle('btn-danger', tutorState.isListening);
}

// --- Existing Functions (Load Plan, Motivation) ---
// (Simplified for brevity, ensuring they integrate with new variables)

async function loadMotivation() {
    try {
        const res = await fetch(`${API_BASE}/ai/motivation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: currentUser.id })
        });
        const data = await res.json();
        motivationTextEl.textContent = `"${data.message}"`;
    } catch (e) { motivationTextEl.textContent = "Keep going!"; }
}

async function loadStats() {
    try {
        // Load Streak
        const streakRes = await fetch(`${API_BASE}/streak?student_id=${currentUser.id}`);
        const streakData = await streakRes.json();
        if (streakData.success) {
            streakCountEl.textContent = streakData.streak.current_streak;
        }

        // Load Progress
        const progressRes = await fetch(`${API_BASE}/progress?student_id=${currentUser.id}`);
        const progressData = await progressRes.json();
        if (progressData.success) {
            progressPercentEl.textContent = `${Math.round(progressData.progress.completion_percentage || 0)}%`;
        }
    } catch (e) {
        console.error("Failed to load stats", e);
    }
}

async function loadTodayPlan() {
    planContainerEl.innerHTML = '<p class="loading-text">Loading...</p>';
    try {
        const res = await fetch(`${API_BASE}/plan/today?student_id=${currentUser.id}`);
        const data = await res.json();
        if (data.success && data.today_plan.length > 0) {
            renderPlanList(data.today_plan);

            // AI Explain logic reuse
            fetch(`${API_BASE}/ai/explain-plan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plan: { date: "Today", total_study_hours: 6, schedule: [{ activities: data.today_plan }] } })
            }).then(r => r.json()).then(d => explanationTextEl.textContent = d.explanation);

        } else {
            planContainerEl.innerHTML = '<p class="empty-state">No plan. Upload syllabus or generate new.</p>';
        }
    } catch (e) { planContainerEl.textContent = "Error loading plan."; }
}

function renderPlanList(tasks) {
    let html = '';
    tasks.forEach(task => {
        const isBreak = task.subject === 'Break';
        const style = isBreak ? 'background: #e9ecef; border-left: 5px solid #28a745;' : '';
        const action = !task.completed && !isBreak ? `<button onclick="completeTask(${task.task_id})" class="btn-secondary">✔</button>` : '';

        html += `
        <div class="plan-item" style="${style} ${task.completed ? 'opacity:0.5' : ''}">
            <div class="plan-time">${task.start_time} - ${task.end_time}</div>
            <div class="plan-details">
                <div class="plan-subject">${task.subject} <span class="tag">${task.difficulty || 'Relax'}</span></div>
                <div class="plan-topic">${task.topics ? task.topics.join(", ") : task.details || ""}</div>
            </div>
            <div class="plan-action">${action}</div>
        </div>`;
    });
    planContainerEl.innerHTML = html;
}

function renderOverallSchedule() {
    if (!overallScheduleCache) {
        planContainerEl.innerHTML = '<p class="empty-state">No overall schedule generated yet.</p>';
        return;
    }
    // Simple Weekly View
    let html = '<h3>Weekly Overview</h3>';
    overallScheduleCache.days.forEach(day => {
        html += `<div style="margin-bottom: 20px;">
            <h4>${day.date}</h4>
            <ul>${day.schedule.map(slot =>
            `<li>${slot.time_slot}: ${slot.activities.map(a => a.subject).join(', ')}</li>`
        ).join('')}</ul>
        </div>`;
    });
    planContainerEl.innerHTML = html;
}

window.completeTask = async function (taskId) {
    await fetch(`${API_BASE}/task/complete/${taskId}?student_id=${currentUser.id}`, { method: 'POST' });
    loadTodayPlan();
    loadStats(); // Update stats after completing task
    loadMotivation(); // Refresh motivation as progress changed
};


