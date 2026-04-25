# 🧠 Adaptive AI Learning Assistant

> An intelligent tutoring system powered by **Google Gemini 2.5 Flash** that teaches, evaluates, and adapts in real-time to your learning pace.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Cloud%20Run-4285F4?style=for-the-badge&logo=google-cloud)](https://adaptive-learning-frontend-442541165615.us-central1.run.app)
[![Backend API](https://img.shields.io/badge/API%20Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger)](https://adaptive-learning-backend-442541165615.us-central1.run.app/docs)

---

## 🚀 Live URLs

| Service | URL |
|---------|-----|
| 🎓 **Frontend App** | https://adaptive-learning-frontend-442541165615.us-central1.run.app |
| ⚙️ **Backend API** | https://adaptive-learning-backend-442541165615.us-central1.run.app |
| 📖 **Swagger Docs** | https://adaptive-learning-backend-442541165615.us-central1.run.app/docs |

---

## ✨ Features

- **Interactive Learning Loop** — AI teaches a concept, gives an example, asks a question, evaluates your answer, and adapts
- **Adaptive Difficulty** — Automatically adjusts based on your rolling accuracy across the last 5 answers
- **Gemini 2.5 Flash** — Powered by Google's latest model via Vertex AI
- **Persistent Sessions** — Progress stored in Firestore (accuracy, difficulty, weak topics)
- **8 Preset Topics** — Derivatives, Linear Algebra, Python, ML, Quantum Physics, Genetics, Statistics, Networking
- **Custom Topics** — Type any topic and the AI will teach it
- **Dark Glassmorphism UI** — Premium dark-mode design with real-time progress indicators

---

## 🧠 Adaptive Logic

| Running Accuracy (last 5 answers) | Action |
|-----------------------------------|--------|
| > 80% | Increase difficulty (max level 5) |
| 50% – 80% | Maintain current difficulty |
| < 50% | Decrease difficulty + use analogies |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI** | Google Gemini 2.5 Flash via Vertex AI |
| **Backend** | Python · FastAPI · Uvicorn |
| **Frontend** | React 18 · Vite 5 |
| **Database** | Google Firestore (Native Mode) |
| **Containerization** | Docker (multi-stage builds) |
| **Deployment** | Google Cloud Run |
| **CI/CD Build** | Google Cloud Build |

---

## 📁 Project Structure

```
learning_assistant/
├── backend/
│   ├── main.py              # FastAPI app — /start-session, /next-step, /evaluate
│   ├── ai_engine.py         # Gemini prompts: teach / evaluate / adapt
│   ├── firestore_client.py  # Firestore CRUD + adaptive scoring logic
│   ├── models.py            # Pydantic request/response models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main state machine + learning loop
│   │   ├── api.js           # Backend API client
│   │   ├── index.css        # Dark glassmorphism design system
│   │   └── components/
│   │       ├── TopicSelector.jsx
│   │       ├── ChatWindow.jsx
│   │       ├── MessageBubble.jsx
│   │       └── ProgressBar.jsx
│   ├── Dockerfile           # nginx-based production image
│   └── package.json
├── cloudbuild.yaml          # Cloud Build pipeline
├── docker-compose.yml       # Local dev orchestration
├── .env.example             # Environment variable template
└── DEPLOYMENT.md            # Full GCP deployment guide
```

---

## ⚡ Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Cloud SDK (`gcloud`)
- GCP project with Vertex AI + Firestore enabled

### 1. Clone & configure

```bash
git clone https://github.com/abhishekdave331/learning_assistant.git
cd learning_assistant
cp .env.example backend/.env
# Edit backend/.env — set GCP_PROJECT_ID
```

### 2. Authenticate with GCP

```bash
gcloud auth application-default login
```

### 3. Run backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

### 4. Run frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

### Or use Docker Compose

```bash
docker-compose up --build
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/start-session` | Create session + first AI lesson |
| `POST` | `/evaluate` | Grade answer + get next adapted lesson |
| `POST` | `/next-step` | Get next lesson without answering |
| `GET` | `/session/{id}` | Get session stats |

---

## ☁️ Deploy to Cloud Run

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the complete step-by-step GCP deployment guide.

```bash
# Build & deploy backend
gcloud builds submit . --config=cloudbuild.yaml --project=YOUR_PROJECT_ID

# Build & deploy frontend
gcloud builds submit ./frontend --tag gcr.io/YOUR_PROJECT/frontend
gcloud run deploy frontend --image gcr.io/YOUR_PROJECT/frontend --allow-unauthenticated
```

---

## 🎓 Example Flow

```
User selects: "Derivatives in Calculus" · Beginner

AI: "A derivative measures how fast something changes...
     Example: speed is the derivative of position.
     Question: What does f'(x) represent?"

User: "It represents the slope of the function at point x"

AI: ✓ 100% — "Perfect! Let's go deeper..."
    [Difficulty increases to Level 2]
```

---

## 📄 License

MIT — feel free to fork and build on it.
