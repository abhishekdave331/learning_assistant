/**
 * API client — wraps all backend calls.
 * In dev, requests go to /api/... which Vite proxies to localhost:8000.
 * In production (Cloud Run), set VITE_API_URL to the backend URL.
 */

const BASE_URL = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/\/$/, '')
  : '/api'

async function request(method, path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const err = await res.json()
      detail = err.detail || detail
    } catch (_) {}
    throw new Error(detail)
  }

  return res.json()
}

/** Create a new learning session */
export function startSession({ userId, topic, skillLevel }) {
  return request('POST', '/start-session', {
    user_id: userId,
    topic,
    skill_level: skillLevel,
  })
}

/** Evaluate a user's answer and get the next lesson */
export function evaluateAnswer({ sessionId, userId, userAnswer }) {
  return request('POST', '/evaluate', {
    session_id: sessionId,
    user_id: userId,
    user_answer: userAnswer,
  })
}

/** Get the next lesson step without answering */
export function getNextStep({ sessionId, userId }) {
  return request('POST', '/next-step', {
    session_id: sessionId,
    user_id: userId,
  })
}

/** Get session stats */
export function getSession(sessionId) {
  return request('GET', `/session/${sessionId}`)
}
