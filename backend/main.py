"""
FastAPI application — Adaptive AI Learning Assistant
Routes: /start-session, /next-step, /evaluate, /session/{id}
"""

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from models import (
    StartSessionRequest,
    StartSessionResponse,
    NextStepRequest,
    NextStepResponse,
    EvaluateRequest,
    EvaluateResponse,
    SessionStats,
    SkillLevel,
)
import firestore_client as fs
import ai_engine as ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Adaptive AI Learning Assistant starting up...")
    yield
    logger.info("🛑 Shutting down...")


app = FastAPI(
    title="Adaptive AI Learning Assistant",
    description="An intelligent tutoring system powered by Gemini and Firestore.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "adaptive-learning-assistant"}


# ─── /start-session ───────────────────────────────────────────────────────────

@app.post("/start-session", response_model=StartSessionResponse)
async def start_session(req: StartSessionRequest):
    """
    Create a new learning session, generate the first AI lesson,
    and persist session data to Firestore.
    """
    difficulty_map = {"beginner": 1, "intermediate": 3, "advanced": 5}
    difficulty = difficulty_map.get(req.skill_level.value, 1)

    logger.info("Starting session for user=%s topic=%s level=%s",
                req.user_id, req.topic, req.skill_level)

    try:
        session_id = fs.create_session(
            user_id=req.user_id,
            topic=req.topic,
            skill_level=req.skill_level.value,
            difficulty=difficulty,
        )
    except Exception as e:
        logger.error("Firestore create_session failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    try:
        message = ai.teach(req.topic, difficulty, weak_topics=[])
    except Exception as e:
        logger.error("Gemini teach failed: %s", e)
        raise HTTPException(status_code=500, detail=f"AI engine error: {e}")

    # Store the initial message as context for evaluation
    fs.update_session(session_id, {"last_ai_message": message})

    return StartSessionResponse(
        session_id=session_id,
        user_id=req.user_id,
        topic=req.topic,
        skill_level=req.skill_level,
        difficulty=difficulty,
        message=message,
        step=0,
    )


# ─── /next-step ───────────────────────────────────────────────────────────────

@app.post("/next-step", response_model=NextStepResponse)
async def next_step(req: NextStepRequest):
    """
    Generate and return the next adapted lesson step for an active session.
    Does NOT require a user answer (used to explicitly request next lesson).
    """
    session = fs.get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    topic = session["topic"]
    difficulty = session.get("difficulty", 1)
    accuracy = session.get("accuracy", 0.0)
    weak_topics = session.get("weak_topics", [])

    try:
        message = ai.adapt(topic, difficulty, accuracy, weak_topics)
    except Exception as e:
        logger.error("Gemini adapt failed: %s", e)
        raise HTTPException(status_code=500, detail=f"AI engine error: {e}")

    new_step = fs.increment_step(req.session_id)
    fs.update_session(req.session_id, {"last_ai_message": message})

    return NextStepResponse(
        session_id=req.session_id,
        message=message,
        difficulty=difficulty,
        step=new_step,
        skill_level=SkillLevel(session.get("skill_level", "beginner")),
        accuracy=accuracy,
    )


# ─── /evaluate ────────────────────────────────────────────────────────────────

@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_answer(req: EvaluateRequest):
    """
    Evaluate a user's answer to the last question, update accuracy,
    adapt difficulty, and return the next lesson step.
    """
    session = fs.get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    topic = session["topic"]
    question_context = session.get("last_ai_message", topic)

    # 1. Evaluate the answer
    try:
        correctness, feedback = ai.evaluate(topic, question_context, req.user_answer)
    except Exception as e:
        logger.error("Gemini evaluate failed: %s", e)
        raise HTTPException(status_code=500, detail=f"AI engine error: {e}")

    # 2. Record answer + adapt difficulty in Firestore
    try:
        updated = fs.record_answer(req.session_id, correctness, topic)
    except Exception as e:
        logger.error("Firestore record_answer failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # 3. Generate next lesson adapted to new difficulty
    try:
        next_message = ai.adapt(
            topic=topic,
            difficulty=updated["difficulty"],
            accuracy=updated["accuracy"],
            weak_topics=updated.get("weak_topics", []),
        )
    except Exception as e:
        logger.error("Gemini adapt failed: %s", e)
        raise HTTPException(status_code=500, detail=f"AI engine error: {e}")

    fs.update_session(req.session_id, {"last_ai_message": next_message})

    return EvaluateResponse(
        session_id=req.session_id,
        correctness=correctness,
        feedback=feedback,
        next_message=next_message,
        difficulty=updated["difficulty"],
        skill_level=SkillLevel(updated["skill_level"]),
        accuracy=updated["accuracy"],
        step=updated["step"],
        weak_topics=updated.get("weak_topics", []),
    )


# ─── /session/{session_id} ────────────────────────────────────────────────────

@app.get("/session/{session_id}", response_model=SessionStats)
async def get_session_stats(session_id: str):
    """Return current session statistics."""
    session = fs.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionStats(
        session_id=session["session_id"],
        user_id=session["user_id"],
        topic=session["topic"],
        step=session.get("step", 0),
        accuracy=session.get("accuracy", 0.0),
        difficulty=session.get("difficulty", 1),
        skill_level=SkillLevel(session.get("skill_level", "beginner")),
        accuracy_history=session.get("accuracy_history", []),
        weak_topics=session.get("weak_topics", []),
    )
