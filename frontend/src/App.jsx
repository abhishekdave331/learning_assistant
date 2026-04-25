/**
 * App.jsx — Adaptive AI Learning Assistant
 * Manages all state and orchestrates the learning loop.
 */
import { useState, useCallback, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'

import TopicSelector from './components/TopicSelector'
import ChatWindow from './components/ChatWindow'
import ProgressBar from './components/ProgressBar'
import { startSession, evaluateAnswer } from './api'

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeMessage(role, content, extra = {}) {
  return { id: uuidv4(), role, content, ...extra }
}

function getUserId() {
  let uid = localStorage.getItem('learn_uid')
  if (!uid) { uid = `user_${uuidv4().slice(0, 8)}`; localStorage.setItem('learn_uid', uid) }
  return uid
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const userId = useRef(getUserId()).current

  // Phase: 'select' | 'learning'
  const [phase, setPhase] = useState('select')

  // Session state
  const [session, setSession] = useState(null)   // { sessionId, topic, skillLevel, difficulty, accuracy, step, weakTopics }
  const [messages, setMessages] = useState([])
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // ── Append helpers ────────────────────────────────────────────────────────

  const pushMsg = useCallback((msg) => setMessages((prev) => [...prev, msg]), [])

  const pushTyping = useCallback(() => {
    const id = uuidv4()
    setMessages((prev) => [...prev, { id, role: 'ai', content: '', isTyping: true }])
    return id
  }, [])

  const replaceTyping = useCallback((typingId, content, extra = {}) => {
    setMessages((prev) => prev.map((m) =>
      m.id === typingId ? { ...m, content, isTyping: false, ...extra } : m
    ))
  }, [])

  // ── Start session ─────────────────────────────────────────────────────────

  async function handleStart({ topic, skillLevel }) {
    setError(null)
    setLoading(true)

    const typingId = pushTyping()

    try {
      const data = await startSession({ userId, topic, skillLevel })

      setSession({
        sessionId: data.session_id,
        topic: data.topic,
        skillLevel: data.skill_level,
        difficulty: data.difficulty,
        accuracy: 0,
        step: data.step,
        weakTopics: [],
      })

      replaceTyping(typingId, data.message)
      setPhase('learning')
    } catch (e) {
      replaceTyping(typingId, '')
      setMessages((prev) => prev.filter((m) => m.id !== typingId))
      setError(`Failed to start session: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  // ── Submit answer ─────────────────────────────────────────────────────────

  async function handleSubmit(e) {
    e?.preventDefault()
    const trimmed = answer.trim()
    if (!trimmed || loading || !session) return

    setAnswer('')
    setError(null)

    // Show user message
    pushMsg(makeMessage('user', trimmed))

    setLoading(true)
    const typingId = pushTyping()

    try {
      const data = await evaluateAnswer({
        sessionId: session.sessionId,
        userId,
        userAnswer: trimmed,
      })

      // Update session state
      setSession((prev) => ({
        ...prev,
        difficulty: data.difficulty,
        skillLevel: data.skill_level,
        accuracy: data.accuracy,
        step: data.step,
        weakTopics: data.weak_topics,
      }))

      // Replace typing with AI response (next lesson)
      replaceTyping(typingId, data.next_message, {
        feedback: data.feedback,
        correctness: data.correctness,
      })
    } catch (e) {
      replaceTyping(typingId, '')
      setMessages((prev) => prev.filter((m) => m.id !== typingId))
      setError(`Evaluation error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  // ── Key handler for textarea ──────────────────────────────────────────────

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // ── New session ───────────────────────────────────────────────────────────

  function resetSession() {
    setPhase('select')
    setSession(null)
    setMessages([])
    setAnswer('')
    setError(null)
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="app-layout">
      {/* Header */}
      <header className="app-header">
        <span className="logo">🧠</span>
        <div className="title-group">
          <h1>Adaptive AI Learning Assistant</h1>
          <p>Powered by Google Gemini · Adapts to your learning pace</p>
        </div>
        {phase === 'learning' && (
          <button className="btn-ghost" onClick={resetSession} style={{ marginLeft: 'auto', fontSize: '0.82rem', padding: '8px 14px' }}>
            ← Back
          </button>
        )}
      </header>

      {/* Topic selector */}
      {phase === 'select' && (
        <TopicSelector onStart={handleStart} loading={loading} />
      )}

      {/* Learning interface */}
      {phase === 'learning' && session && (
        <>
          {/* Progress */}
          <ProgressBar
            skillLevel={session.skillLevel}
            difficulty={session.difficulty}
            accuracy={session.accuracy}
            step={session.step}
            weakTopics={session.weakTopics}
          />

          {/* Session bar */}
          <div className="session-bar">
            <div className="topic-chip">
              📚 <span>{session.topic}</span>
            </div>
            <div className="step-count">
              💬 {messages.filter((m) => m.role !== 'system').length} messages
            </div>
            <button className="new-session-btn" onClick={resetSession}>
              ✕ New session
            </button>
          </div>

          {/* Error */}
          {error && (
            <div className="error-banner" role="alert">
              ⚠️ {error}
            </div>
          )}

          {/* Chat */}
          <div className="chat-section">
            <ChatWindow messages={messages} />

            {/* Input */}
            <div className="input-area">
              <form onSubmit={handleSubmit} className="input-row">
                <textarea
                  id="answer-input"
                  className="chat-input"
                  placeholder="Type your answer… (Enter to send, Shift+Enter for new line)"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                  rows={1}
                  style={{ height: 'auto' }}
                  onInput={(e) => {
                    e.target.style.height = 'auto'
                    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px'
                  }}
                />
                <button
                  id="send-btn"
                  type="submit"
                  className="send-btn"
                  disabled={!answer.trim() || loading}
                  aria-label="Send answer"
                >
                  {loading ? (
                    <span style={{ fontSize: '0.7rem' }}>⏳</span>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13" />
                      <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                  )}
                </button>
              </form>
              <p className="hint-text">
                AI evaluates your response and adapts difficulty in real-time
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
