"""Firestore CRUD helpers for session management and user profiles."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from google.cloud import firestore

_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db


# ─── Session helpers ──────────────────────────────────────────────────────────

def create_session(
    user_id: str,
    topic: str,
    skill_level: str,
    difficulty: int = 1,
) -> str:
    """Create a new learning session in Firestore. Returns session_id."""
    db = get_db()
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "topic": topic,
        "skill_level": skill_level,
        "difficulty": difficulty,
        "step": 0,
        "accuracy_history": [],
        "weak_topics": [],
        "accuracy": 0.0,
        "created_at": now,
        "updated_at": now,
    }

    db.collection("sessions").document(session_id).set(session_data)
    _upsert_user_profile(user_id, topic, skill_level)
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a session document."""
    db = get_db()
    doc = db.collection("sessions").document(session_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def update_session(
    session_id: str,
    updates: Dict[str, Any],
) -> None:
    """Partial-update a session document."""
    db = get_db()
    updates["updated_at"] = datetime.now(timezone.utc)
    db.collection("sessions").document(session_id).update(updates)


def record_answer(
    session_id: str,
    correctness: float,
    topic: str,
) -> Dict[str, Any]:
    """
    Record a user answer, update accuracy history, recalculate accuracy,
    adapt difficulty, and return updated session state.
    """
    db = get_db()
    session = get_session(session_id)
    if session is None:
        raise ValueError(f"Session {session_id} not found")

    # Update accuracy history (rolling window of last 5)
    history: List[float] = session.get("accuracy_history", [])
    history.append(correctness)
    history = history[-5:]  # keep last 5

    accuracy = sum(history) / len(history)
    difficulty = session.get("difficulty", 1)
    weak_topics: List[str] = session.get("weak_topics", [])

    # Adaptive logic
    if accuracy > 0.8:
        difficulty = min(difficulty + 1, 5)
    elif accuracy < 0.5:
        difficulty = max(difficulty - 1, 1)
        if topic not in weak_topics:
            weak_topics.append(topic)

    # Derive skill level
    skill_level = _difficulty_to_skill(difficulty)

    updates = {
        "accuracy_history": history,
        "accuracy": accuracy,
        "difficulty": difficulty,
        "skill_level": skill_level,
        "weak_topics": weak_topics,
        "step": session.get("step", 0) + 1,
    }
    update_session(session_id, updates)

    return {**session, **updates}


def increment_step(session_id: str) -> int:
    """Increment session step counter. Returns new step number."""
    session = get_session(session_id)
    if session is None:
        raise ValueError(f"Session {session_id} not found")
    new_step = session.get("step", 0) + 1
    update_session(session_id, {"step": new_step})
    return new_step


# ─── User profile helpers ─────────────────────────────────────────────────────

def _upsert_user_profile(user_id: str, topic: str, skill_level: str) -> None:
    db = get_db()
    ref = db.collection("users").document(user_id)
    doc = ref.get()
    now = datetime.now(timezone.utc)

    if doc.exists:
        ref.update({
            "last_topic": topic,
            "last_skill_level": skill_level,
            "updated_at": now,
        })
    else:
        ref.set({
            "user_id": user_id,
            "last_topic": topic,
            "last_skill_level": skill_level,
            "created_at": now,
            "updated_at": now,
        })


# ─── Utilities ────────────────────────────────────────────────────────────────

def _difficulty_to_skill(difficulty: int) -> str:
    if difficulty <= 2:
        return "beginner"
    elif difficulty <= 4:
        return "intermediate"
    return "advanced"
