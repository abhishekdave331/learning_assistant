/**
 * MessageBubble — Single chat message with markdown rendering.
 */
import ReactMarkdown from 'react-markdown'

function ScorePill({ score }) {
  const pct = Math.round(score * 100)
  const cls = score >= 0.8 ? 'high' : score >= 0.5 ? 'mid' : 'low'
  const emoji = score >= 0.8 ? '✓' : score >= 0.5 ? '~' : '✗'
  return (
    <span className={`score-pill ${cls}`}>
      {emoji} {pct}%
    </span>
  )
}

function FeedbackChip({ correctness, feedback }) {
  const cls = correctness >= 0.8 ? 'correct' : correctness >= 0.5 ? 'neutral' : 'incorrect'
  const icon = correctness >= 0.8 ? '🎉' : correctness >= 0.5 ? '💡' : '🔄'
  return (
    <div className={`feedback-bubble ${cls}`}>
      <span>{icon}</span>
      <span>{feedback}</span>
      <ScorePill score={correctness} />
    </div>
  )
}

export default function MessageBubble({ message }) {
  const { role, content, feedback, correctness, isTyping } = message

  if (role === 'system') {
    return (
      <div className="msg-wrapper">
        <div className="msg-bubble system">{content}</div>
      </div>
    )
  }

  const isAI = role === 'ai'

  return (
    <div className={`msg-wrapper ${isAI ? 'ai' : 'user'}`}>
      <div className={`msg-avatar ${isAI ? 'ai' : 'user'}`}>
        {isAI ? '🧠' : '👤'}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: '75%' }}>
        <div className={`msg-bubble ${isAI ? 'ai' : 'user'}`}>
          {isTyping ? (
            <div className="typing-dots">
              <span /><span /><span />
            </div>
          ) : (
            <div className="msg-content">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
        </div>
        {feedback && correctness !== undefined && (
          <FeedbackChip correctness={correctness} feedback={feedback} />
        )}
      </div>
    </div>
  )
}
