"""Pydantic request/response models for the Adaptive AI Learning Assistant."""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class StartSessionRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    topic: str = Field(..., description="Topic to learn (e.g., 'derivatives')")
    skill_level: SkillLevel = Field(SkillLevel.beginner, description="Starting skill level")


class StartSessionResponse(BaseModel):
    session_id: str
    user_id: str
    topic: str
    skill_level: SkillLevel
    difficulty: int = Field(description="Current difficulty level 1-5")
    message: str = Field(description="AI-generated lesson content")
    step: int = 0


class NextStepRequest(BaseModel):
    session_id: str
    user_id: str


class NextStepResponse(BaseModel):
    session_id: str
    message: str
    difficulty: int
    step: int
    skill_level: SkillLevel
    accuracy: float


class EvaluateRequest(BaseModel):
    session_id: str
    user_id: str
    user_answer: str


class EvaluateResponse(BaseModel):
    session_id: str
    correctness: float = Field(description="Score from 0.0 to 1.0")
    feedback: str = Field(description="Short one-line feedback")
    next_message: str = Field(description="Next lesson step from AI")
    difficulty: int
    skill_level: SkillLevel
    accuracy: float = Field(description="Running accuracy (last 5 answers)")
    step: int
    weak_topics: List[str] = []


class SessionStats(BaseModel):
    session_id: str
    user_id: str
    topic: str
    step: int
    accuracy: float
    difficulty: int
    skill_level: SkillLevel
    accuracy_history: List[float]
    weak_topics: List[str]
