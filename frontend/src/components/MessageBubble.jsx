import { useState } from 'react'

/**
 * Message Bubble Component
 * Renders individual chat messages with formatting
 */
function MessageBubble({ message }) {
  const [showDetails, setShowDetails] = useState(false)
  const isUser = message.type === 'user'
  const isError = message.isError

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`message-bubble ${
          isUser 
            ? 'message-user' 
            : isError 
              ? 'bg-red-50 border-red-200 text-red-800' 
              : 'message-bot'
        }`}
      >
        {/* Message Content */}
        <div className="markdown-content">
          <FormattedContent content={message.content} />
        </div>

        {/* Bot Message Extras */}
        {!isUser && !isError && message.score !== undefined && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            {/* Score Badge */}
            <div className="flex items-center gap-3 flex-wrap">
              <ScoreBadge score={message.score} />
              <ConfidenceIndicator confidence={message.confidence} />
            </div>

            {/* Details Toggle */}
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="mt-2 text-xs text-primary-600 hover:text-primary-800 flex items-center gap-1"
            >
              {showDetails ? '▲ Hide details' : '▼ Show details'}
            </button>

            {/* Expanded Details */}
            {showDetails && (
              <div className="mt-3 space-y-3 text-sm animate-slide-down">
                {/* Assumptions */}
                {message.assumptions && (
                  <DetailSection 
                    title="📝 Assumptions Made" 
                    content={message.assumptions}
                  />
                )}

                {/* Improvements */}
                {message.improvements && (
                  <DetailSection 
                    title="💡 Suggestions" 
                    content={message.improvements}
                  />
                )}

                {/* Extracted Entities */}
                {message.entitiesExtracted && (
                  <EntitiesSection entities={message.entitiesExtracted} />
                )}

                {/* Context Indicator */}
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{message.contextUsed ? '✅' : '❌'}</span>
                  <span>
                    {message.contextUsed 
                      ? 'Based on property data' 
                      : 'General knowledge response'
                    }
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className={`mt-2 text-xs ${isUser ? 'text-primary-200' : 'text-gray-400'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  )
}

/**
 * Score Badge Component
 */
function ScoreBadge({ score }) {
  const getScoreClass = (score) => {
    if (score >= 7) return 'score-high'
    if (score >= 4) return 'score-medium'
    return 'score-low'
  }

  return (
    <div className={`score-badge ${getScoreClass(score)}`}>
      Score: {score}/10
    </div>
  )
}

/**
 * Confidence Indicator Component
 */
function ConfidenceIndicator({ confidence }) {
  if (confidence === undefined || confidence === null) return null

  const percentage = Math.round(confidence * 100)
  const getLabel = (conf) => {
    if (conf >= 0.7) return { text: 'High', color: 'text-green-600' }
    if (conf >= 0.4) return { text: 'Medium', color: 'text-yellow-600' }
    return { text: 'Low', color: 'text-red-600' }
  }

  const { text, color } = getLabel(confidence)

  return (
    <div className="flex items-center gap-1 text-xs">
      <span className="text-gray-500">Confidence:</span>
      <span className={`font-medium ${color}`}>{text} ({percentage}%)</span>
    </div>
  )
}

/**
 * Detail Section Component
 */
function DetailSection({ title, content }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <h4 className="font-medium text-gray-700 mb-1">{title}</h4>
      <p className="text-gray-600">{content}</p>
    </div>
  )
}

/**
 * Entities Section Component
 */
function EntitiesSection({ entities }) {
  const hasEntities = entities.location || entities.price || entities.area || entities.bhk

  if (!hasEntities) return null

  return (
    <div className="bg-blue-50 rounded-lg p-3">
      <h4 className="font-medium text-blue-700 mb-2">🔍 Extracted Information</h4>
      <div className="flex flex-wrap gap-2">
        {entities.location && (
          <EntityChip label="Location" value={entities.location} />
        )}
        {entities.price && (
          <EntityChip label="Price" value={`${entities.price} ${entities.price_unit || 'Cr'}`} />
        )}
        {entities.area && (
          <EntityChip label="Area" value={`${entities.area} ${entities.area_unit || 'sq ft'}`} />
        )}
        {entities.bhk && (
          <EntityChip label="BHK" value={entities.bhk} />
        )}
      </div>
    </div>
  )
}

/**
 * Entity Chip Component
 */
function EntityChip({ label, value }) {
  return (
    <span className="inline-flex items-center gap-1 bg-white px-2 py-1 rounded text-xs">
      <span className="text-gray-500">{label}:</span>
      <span className="font-medium text-blue-700">{value}</span>
    </span>
  )
}

/**
 * Formatted Content Component
 * Simple markdown-like formatting
 */
function FormattedContent({ content }) {
  if (!content) return null

  // Split by double newlines for paragraphs
  const paragraphs = content.split('\n\n')

  return (
    <>
      {paragraphs.map((paragraph, index) => (
        <div key={index} className="mb-2 last:mb-0">
          {formatParagraph(paragraph)}
        </div>
      ))}
    </>
  )
}

/**
 * Format a single paragraph
 */
function formatParagraph(text) {
  // Handle bullet points
  if (text.includes('\n-') || text.startsWith('-')) {
    const lines = text.split('\n')
    return (
      <ul className="list-disc list-inside space-y-1">
        {lines.map((line, i) => {
          const cleanLine = line.replace(/^-\s*/, '')
          return cleanLine ? <li key={i}>{formatInline(cleanLine)}</li> : null
        })}
      </ul>
    )
  }

  // Handle numbered lists
  if (text.match(/^\d+\./)) {
    const lines = text.split('\n')
    return (
      <ol className="list-decimal list-inside space-y-1">
        {lines.map((line, i) => {
          const cleanLine = line.replace(/^\d+\.\s*/, '')
          return cleanLine ? <li key={i}>{formatInline(cleanLine)}</li> : null
        })}
      </ol>
    )
  }

  // Regular paragraph
  return <p>{formatInline(text)}</p>
}

/**
 * Format inline elements (bold, code, etc.)
 */
function formatInline(text) {
  // Replace **bold** with <strong>
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>
    }
    return part
  })
}

/**
 * Format timestamp
 */
function formatTime(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default MessageBubble
