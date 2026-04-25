# Adaptive AI Learning Assistant

An intelligent tutoring system powered by Google Gemini and Firestore that teaches, evaluates, and adapts in real-time.

---

## Project Structure

```
learning_assistant/
├── backend/            FastAPI backend
├── frontend/           React (Vite) frontend
├── docker-compose.yml  Local dev orchestration
├── .env.example        Environment variable template
└── DEPLOYMENT.md       This file
```

---

## Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.11+ |
| Node.js | 20.x |
| Docker | 24+ |
| Google Cloud SDK (`gcloud`) | Latest |

---

## Google Cloud Setup

### 1. Enable APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  --project YOUR_PROJECT_ID
```

### 2. Create Firestore (Native Mode)

```bash
gcloud firestore databases create \
  --location=us-central \
  --project YOUR_PROJECT_ID
```

### 3. Create Service Account (for local dev)

```bash
gcloud iam service-accounts create learning-assistant-sa \
  --display-name="Learning Assistant SA" \
  --project YOUR_PROJECT_ID

# Grant roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:learning-assistant-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:learning-assistant-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# Download key
gcloud iam service-accounts keys create service-account.json \
  --iam-account=learning-assistant-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

## Local Development

### Option A: Native Python + Node

```bash
# 1. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp ../.env.example ../.env
# Edit .env and fill in GCP_PROJECT_ID

# 3. Authenticate (choose one):
#   a) Service account key:
export GOOGLE_APPLICATION_CREDENTIALS=../service-account.json
#   b) Application Default Credentials:
gcloud auth application-default login

# 4. Run backend
uvicorn main:app --reload --port 8000

# 5. In a new terminal — run frontend
cd ../frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Option B: Docker Compose

```bash
# Copy and edit .env
cp .env.example .env
# Edit .env with your GCP_PROJECT_ID

# Place service-account.json in project root
# Then run:
docker-compose up --build

# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000
# API docs:  http://localhost:8000/docs
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/start-session` | Create session + first lesson |
| POST | `/evaluate` | Grade answer + get next lesson |
| POST | `/next-step` | Skip to next lesson |
| GET | `/session/{id}` | Get session stats |

**Interactive Swagger docs**: `http://localhost:8000/docs`

---

## Deploy Backend to Cloud Run

### 1. Build & push container

```bash
export PROJECT_ID=your-project-id
export REGION=us-central1
export SERVICE=adaptive-learning-backend

# Build with Cloud Build
gcloud builds submit ./backend \
  --tag gcr.io/$PROJECT_ID/$SERVICE \
  --project $PROJECT_ID
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy $SERVICE \
  --image gcr.io/$PROJECT_ID/$SERVICE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_LOCATION=$REGION,GEMINI_MODEL=gemini-1.5-flash-001" \
  --service-account=learning-assistant-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --project $PROJECT_ID
```

### 3. Get the service URL

```bash
gcloud run services describe $SERVICE \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)'
```

### 4. Update frontend API URL

```bash
# In frontend/.env (or set at build time)
VITE_API_URL=https://<your-cloud-run-url>
```

---

## Deploy Frontend

### Option A: Static build + Firebase Hosting

```bash
cd frontend
npm run build

# Install Firebase CLI
npm install -g firebase-tools
firebase login
firebase init hosting   # choose frontend/dist as public dir
firebase deploy
```

### Option B: Serve from Cloud Run (containerized)

Create `frontend/Dockerfile.prod`:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
gcloud builds submit ./frontend \
  --tag gcr.io/$PROJECT_ID/learning-assistant-frontend \
  --build-arg VITE_API_URL=https://<backend-url>

gcloud run deploy learning-assistant-frontend \
  --image gcr.io/$PROJECT_ID/learning-assistant-frontend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated
```

---

## Sample Test Flow (curl)

```bash
BASE=https://<your-cloud-run-url>

# 1. Start a session
SESSION=$(curl -s -X POST $BASE/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","topic":"derivatives in calculus","skill_level":"beginner"}')
echo $SESSION | python3 -m json.tool
SESSION_ID=$(echo $SESSION | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

# 2. Answer the question
curl -s -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_id\":\"demo\",\"user_answer\":\"A derivative measures how fast a function changes.\"}" \
  | python3 -m json.tool

# 3. Check session stats
curl -s $BASE/session/$SESSION_ID | python3 -m json.tool
```

---

## Adaptive Logic Summary

| Running Accuracy | Action |
|-----------------|--------|
| > 80% | Increase difficulty (max 5) |
| 50–80% | Maintain current difficulty |
| < 50% | Decrease difficulty + use analogies |

Accuracy is calculated as a rolling average of the **last 5 answers**.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `google.auth.exceptions.DefaultCredentialsError` | Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS` |
| `404 Firestore collection` | Ensure Firestore is in **Native Mode** (not Datastore) |
| `400 Model not found` | Check `GEMINI_MODEL` and `GCP_LOCATION` — gemini-1.5-flash requires `us-central1` |
| Frontend CORS error | Ensure backend has CORS enabled (it does) and `VITE_API_URL` is correct |
