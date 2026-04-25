/**
 * TopicSelector — Initial screen for choosing a topic and skill level.
 */
import { useState } from 'react'

const PRESET_TOPICS = [
  { icon: '∂', label: 'Derivatives',    sub: 'Calculus',        topic: 'derivatives in calculus' },
  { icon: '∑', label: 'Linear Algebra', sub: 'Mathematics',     topic: 'linear algebra fundamentals' },
  { icon: '🐍', label: 'Python',         sub: 'Programming',     topic: 'Python programming basics' },
  { icon: '🤖', label: 'Machine Learning', sub: 'AI/ML',         topic: 'machine learning concepts' },
  { icon: '⚛️', label: 'Quantum Physics', sub: 'Physics',        topic: 'quantum physics principles' },
  { icon: '🧬', label: 'DNA & Genetics', sub: 'Biology',         topic: 'DNA and genetics' },
  { icon: '📈', label: 'Statistics',    sub: 'Data Science',    topic: 'statistics and probability' },
  { icon: '🌐', label: 'Networking',    sub: 'Computer Science', topic: 'computer networking fundamentals' },
]

const SKILL_LEVELS = [
  { value: 'beginner',     label: '🌱 Beginner' },
  { value: 'intermediate', label: '⚡ Intermediate' },
  { value: 'advanced',     label: '🚀 Advanced' },
]

export default function TopicSelector({ onStart, loading }) {
  const [customTopic, setCustomTopic] = useState('')
  const [skillLevel, setSkillLevel] = useState('beginner')
  const [selectedTopic, setSelectedTopic] = useState(null)

  function handlePreset(topic) {
    setSelectedTopic(topic.topic)
    setCustomTopic('')
  }

  function handleStart() {
    const topic = customTopic.trim() || selectedTopic
    if (!topic) return
    onStart({ topic, skillLevel })
  }

  const activeTopic = customTopic.trim() || selectedTopic
  const canStart = !!activeTopic && !loading

  return (
    <div className="topic-page">
      <div className="topic-hero">
        <h2>What do you want to learn today?</h2>
        <p>Pick a topic and let AI guide you step by step at your own pace.</p>
      </div>

      {/* Preset topic grid */}
      <div className="topic-grid">
        {PRESET_TOPICS.map((t) => (
          <button
            key={t.topic}
            className="topic-card"
            id={`topic-${t.label.toLowerCase().replace(/\s+/g, '-')}`}
            onClick={() => handlePreset(t)}
            style={{
              borderColor: selectedTopic === t.topic ? 'var(--accent-purple)' : '',
              boxShadow: selectedTopic === t.topic ? 'var(--shadow-glow)' : '',
            }}
          >
            <span className="tc-icon">{t.icon}</span>
            <span className="tc-label">{t.label}</span>
            <span className="tc-sub">{t.sub}</span>
          </button>
        ))}
      </div>

      {/* Custom topic */}
      <div className="custom-topic-form">
        <input
          id="custom-topic-input"
          className="custom-topic-input"
          type="text"
          placeholder="Or type your own topic… e.g. 'Big Bang Theory'"
          value={customTopic}
          onChange={(e) => { setCustomTopic(e.target.value); setSelectedTopic(null) }}
          onKeyDown={(e) => e.key === 'Enter' && canStart && handleStart()}
        />
      </div>

      {/* Skill level */}
      <div>
        <p style={{ textAlign: 'center', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 10 }}>
          Select your starting level
        </p>
        <div className="skill-selector">
          {SKILL_LEVELS.map((s) => (
            <button
              key={s.value}
              id={`skill-${s.value}`}
              className={`skill-btn ${skillLevel === s.value ? 'active' : ''}`}
              onClick={() => setSkillLevel(s.value)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Start button */}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <button
          id="start-learning-btn"
          className="btn-primary"
          disabled={!canStart}
          onClick={handleStart}
          style={{ padding: '14px 40px', fontSize: '1rem' }}
        >
          {loading ? (
            <>
              <span className="typing-dots">
                <span /><span /><span />
              </span>
              Starting…
            </>
          ) : (
            <>🚀 Start Learning</>
          )}
        </button>
      </div>
    </div>
  )
}
