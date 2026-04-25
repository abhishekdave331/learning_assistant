/**
 * ProgressBar — Shows current learning progress and difficulty.
 */

const LEVEL_LABELS = ['1', '2', '3', '4', '5']

export default function ProgressBar({ skillLevel, difficulty, accuracy, step, weakTopics = [] }) {
  // Progress fills based on difficulty out of 5
  const fillPct = Math.min(((difficulty - 1) / 4) * 100, 100)
  const accuracyPct = Math.round(accuracy * 100)

  return (
    <div className="progress-section">
      {/* Info row */}
      <div className="progress-row">
        <div className="progress-labels">
          <span className={`level-badge ${skillLevel}`}>
            {skillLevel === 'beginner' ? '🌱' : skillLevel === 'intermediate' ? '⚡' : '🚀'}{' '}
            {skillLevel}
          </span>
          <div className="diff-indicator" title="Current difficulty (1–5)">
            {LEVEL_LABELS.map((l, i) => (
              <div
                key={l}
                className={`diff-dot ${i < difficulty ? 'active' : ''}`}
              />
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <span className="accuracy-label">
            Accuracy <span>{accuracyPct}%</span>
          </span>
          <span className="accuracy-label">
            Step <span>#{step}</span>
          </span>
        </div>
      </div>

      {/* Progress track */}
      <div className="progress-track" title={`Difficulty level ${difficulty}/5`}>
        <div className="progress-fill" style={{ width: `${fillPct}%` }} />
      </div>

      {/* Weak topics */}
      {weakTopics.length > 0 && (
        <div className="weak-topics" style={{ marginTop: 8 }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Needs review:</span>
          {weakTopics.map((t) => (
            <span key={t} className="weak-tag">{t}</span>
          ))}
        </div>
      )}
    </div>
  )
}
