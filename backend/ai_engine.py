"""
Vertex AI (Gemini) integration for the Adaptive AI Learning Assistant.

Three prompt modes:
  - teach:    Structured lesson + example + question at a given difficulty
  - evaluate: Grade a user's answer (0–1 score + one-line feedback)
  - adapt:    Generate the next lesson adapted to performance
"""

import json
import os
import re
import logging
from typing import Tuple

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

logger = logging.getLogger(__name__)

_model: GenerativeModel | None = None


def _get_model() -> GenerativeModel:
    global _model
    if _model is None:
        project = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        vertexai.init(project=project, location=location)
        _model = GenerativeModel(model_name)
    return _model


# ─── Prompt builders ──────────────────────────────────────────────────────────

def _teach_prompt(topic: str, difficulty: int, weak_topics: list[str]) -> str:
    level_label = {1: "complete beginner", 2: "beginner", 3: "intermediate",
                   4: "advanced", 5: "expert"}.get(difficulty, "beginner")

    weak_note = ""
    if weak_topics:
        weak_note = (
            f"\nThe learner struggles with: {', '.join(weak_topics)}. "
            "Be extra clear and use a relatable analogy."
        )

    analogy_note = ""
    if difficulty <= 2:
        analogy_note = " Use a simple real-world analogy to explain the concept."

    return f"""You are an expert, friendly tutor teaching a {level_label} learner.
Topic: {topic}{weak_note}

Instructions:
1. Explain the concept clearly in under 5 lines.{analogy_note}
2. Give exactly ONE concrete example (label it "Example:").
3. Ask exactly ONE question to test understanding (label it "Question:").

Keep your response concise and structured. Do NOT use markdown headers."""


def _evaluate_prompt(topic: str, question_context: str, user_answer: str) -> str:
    return f"""You are grading a student's answer on the topic: {topic}.

The student was asked:
\"\"\"{question_context}\"\"\"

The student answered:
\"\"\"{user_answer}\"\"\"

Respond ONLY with valid JSON (no markdown, no extra text) in this exact format:
{{
  "correctness": <float between 0.0 and 1.0>,
  "feedback": "<one-line encouraging feedback>"
}}"""


def _adapt_prompt(
    topic: str,
    difficulty: int,
    accuracy: float,
    weak_topics: list[str],
) -> str:
    if accuracy > 0.8:
        adaptation = (
            f"The learner is doing very well (accuracy={accuracy:.0%}). "
            "Increase the challenge — ask a harder conceptual or application-level question."
        )
    elif accuracy < 0.5:
        adaptation = (
            f"The learner is struggling (accuracy={accuracy:.0%}). "
            "Simplify using a different analogy. Break the explanation into even smaller steps."
        )
    else:
        adaptation = (
            f"The learner is making steady progress (accuracy={accuracy:.0%}). "
            "Continue at the same depth with a fresh angle on the topic."
        )

    weak_note = ""
    if weak_topics:
        weak_note = f" Focus more on: {', '.join(weak_topics)}."

    level_label = {1: "complete beginner", 2: "beginner", 3: "intermediate",
                   4: "advanced", 5: "expert"}.get(difficulty, "beginner")

    return f"""You are an adaptive AI tutor. {adaptation}{weak_note}

Topic: {topic}
Current difficulty level: {difficulty}/5 ({level_label})

Instructions:
1. Teach the next concept or deepen the current one (under 5 lines).
2. Give exactly ONE example (label it "Example:").
3. Ask exactly ONE follow-up question (label it "Question:").

Be concise, warm, and encouraging. Do NOT use markdown headers."""


# ─── Public API ───────────────────────────────────────────────────────────────

def teach(topic: str, difficulty: int, weak_topics: list[str] | None = None) -> str:
    """Generate an initial lesson for a topic at a given difficulty level."""
    model = _get_model()
    prompt = _teach_prompt(topic, difficulty, weak_topics or [])
    config = GenerationConfig(temperature=0.7, max_output_tokens=512)
    response = model.generate_content(prompt, generation_config=config)
    return response.text.strip()


def evaluate(
    topic: str,
    question_context: str,
    user_answer: str,
) -> Tuple[float, str]:
    """
    Evaluate a user's answer.
    Returns (correctness: 0.0–1.0, feedback: str).
    """
    model = _get_model()
    prompt = _evaluate_prompt(topic, question_context, user_answer)
    config = GenerationConfig(temperature=0.2, max_output_tokens=256)
    response = model.generate_content(prompt, generation_config=config)
    raw = response.text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        correctness = float(data.get("correctness", 0.5))
        feedback = str(data.get("feedback", "Keep going!"))
        correctness = max(0.0, min(1.0, correctness))
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Evaluate parse error (%s). Raw: %s", e, raw)
        correctness = 0.5
        feedback = "Good attempt! Keep practicing."

    return correctness, feedback


def adapt(
    topic: str,
    difficulty: int,
    accuracy: float,
    weak_topics: list[str] | None = None,
) -> str:
    """Generate the next adaptive lesson step based on performance."""
    model = _get_model()
    prompt = _adapt_prompt(topic, difficulty, accuracy, weak_topics or [])
    config = GenerationConfig(temperature=0.75, max_output_tokens=512)
    response = model.generate_content(prompt, generation_config=config)
    return response.text.strip()
