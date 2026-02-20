import { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import Loader from './Loader'

/**
 * Chat Window Component
 * Displays all chat messages with auto-scroll
 */
function ChatWindow({ messages, isLoading, error, onClearError }) {
  const messagesEndRef = useRef(null)
  const containerRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isLoading])

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-hide"
    >
      {/* Empty State */}
      {messages.length === 0 && !isLoading && (
        <EmptyState />
      )}

      {/* Messages */}
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex justify-start">
          <div className="message-bubble message-bot">
            <Loader />
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
          <span className="text-red-500">⚠️</span>
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button 
            onClick={onClearError}
            className="text-red-400 hover:text-red-600"
          >
            ✕
          </button>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  )
}

/**
 * Empty State Component
 */
function EmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-6 py-12">
      <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl flex items-center justify-center mb-6">
        <span className="text-4xl">🏠</span>
      </div>
      
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Welcome to Real Estate Tutor!
      </h2>
      
      <p className="text-gray-500 mb-6 max-w-sm">
        Ask me anything about real estate - property prices, area calculations, 
        investment advice, or RERA regulations.
      </p>
      
      <div className="bg-gray-50 rounded-xl p-4 max-w-sm">
        <p className="text-sm text-gray-600 mb-2">
          <strong>Try asking:</strong>
        </p>
        <ul className="text-sm text-gray-500 space-y-1">
          <li>• "700 sq ft Parel worth 2.1 Cr?"</li>
          <li>• "What's carpet area?"</li>
          <li>• "Is Powai good for investment?"</li>
        </ul>
      </div>
      
      <p className="text-xs text-gray-400 mt-6">
        Tip: Use quick actions below for common questions
      </p>
    </div>
  )
}

export default ChatWindow
