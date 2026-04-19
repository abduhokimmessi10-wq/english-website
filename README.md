# SpeakAI — IELTS Speaking Practice

AI-powered IELTS speaking practice platform with Groq AI feedback.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.12 + Django 4.2          |
| API        | Django REST Framework             |
| Database   | PostgreSQL                        |
| AI         | Groq API (llama3-70b-8192)        |
| Frontend   | HTML5 + CSS3 + Vanilla JavaScript |
| Voice      | Web Speech API (Chrome)           |

---

## Features

- Part 1 — 20 conversational questions
- Part 2 — 20 cue card monologue prompts
- Part 3 — 20 analytical discussion questions
- Voice recording via microphone (Chrome)
- Text input alternative
- AI feedback: Fluency, Vocabulary, Grammar, Pronunciation
- Band score (1.0 – 9.0)
- Strengths + improvements + Band 9 model answer
- Session history and results page
- PostgreSQL database storage

---

## Setup (Windows)

### Step 1 — Enter project folder
```powershell
cd ielts
```

### Step 2 — Create and activate virtual environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4 — Create .env file
Copy `.env.example` to `.env` and fill in your values:
```powershell
copy .env.example .env
```

Edit `.env`:
```
SECRET_KEY=django-insecure-ielts-speaking-change-in-production
DEBUG=True
DB_NAME=ielts_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### Step 5 — Create PostgreSQL database
In pgAdmin or psql:
```sql
CREATE DATABASE ielts_db;
```

### Step 6 — Run migrations
```powershell
python manage.py migrate
```

### Step 7 — Load questions
```powershell
python manage.py load_questions
```

### Step 8 — Create admin user (optional)
```powershell
python manage.py createsuperuser
```

### Step 9 — Run server
```powershell
python manage.py runserver 8001
```

Open: http://127.0.0.1:8001

---

## API Endpoints

| Method | URL                              | Description              |
|--------|----------------------------------|--------------------------|
| GET    | `/`                              | Homepage                 |
| GET    | `/practice/<part>/`              | Practice page (1, 2, 3)  |
| GET    | `/results/<session_id>/`         | Session results          |
| GET    | `/api/questions/<part>/`         | Get questions for a part |
| POST   | `/api/session/start/`            | Start a new session      |
| POST   | `/api/session/<id>/complete/`    | Complete session         |
| POST   | `/api/answer/submit/`            | Submit answer + get AI   |
| GET    | `/api/history/`                  | Session history          |
| GET    | `/admin/`                        | Django admin panel       |

---

## Project Structure

```
ielts/
├── ielts/                   Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── speaking/                Main app
│   ├── models.py            Question, PracticeSession, Answer
│   ├── views.py             Page views + REST API
│   ├── urls.py
│   ├── admin.py
│   ├── ai_feedback.py       Groq AI integration
│   ├── questions_data.py    60 IELTS questions (20 per part)
│   └── management/
│       └── commands/
│           └── load_questions.py
├── templates/
│   ├── base.html            Base layout + nav
│   ├── index.html           Homepage
│   ├── practice.html        Practice page (voice + text + AI)
│   └── results.html         Session results
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Voice Recording

Voice recording uses the **Web Speech API** built into Chrome.
- Works best in **Google Chrome** or **Microsoft Edge**
- Firefox and Safari have limited support
- The transcript appears in real time as you speak
- Click stop when finished, then click "Get AI Feedback"
