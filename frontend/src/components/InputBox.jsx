import { useState, useRef, useEffect } from 'react'

/**
 * Input Box Component
 * Chat input with send button and character limit
 */
function InputBox({ onSend, isLoading, placeholder = "Type your question..." }) {
  const [message, setMessage] = useState('')
  const inputRef = useRef(null)
  const maxLength = 500

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (message.trim() && !isLoading) {
      onSend(message.trim())
      setMessage('')
    }
  }

  // Handle key press (Enter to send)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const remainingChars = maxLength - message.length
  const isNearLimit = remainingChars < 50

  return (
    <form 
      onSubmit={handleSubmit}
      className="bg-white border-t border-gray-200 px-4 py-3 pb-safe"
    >
      <div className="flex items-center gap-2">
        {/* Input Field */}
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value.slice(0, maxLength))}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={isLoading}
            className="chat-input pr-16"
            aria-label="Chat message input"
          />
          
          {/* Character Counter */}
          {message.length > 0 && (
            <span 
              className={`absolute right-4 top-1/2 -translate-y-1/2 text-xs ${
                isNearLimit ? 'text-orange-500' : 'text-gray-400'
              }`}
            >
              {remainingChars}
            </span>
          )}
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim() || isLoading}
          className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 ${
            message.trim() && !isLoading
              ? 'bg-primary-600 hover:bg-primary-700 text-white shadow-lg shadow-primary-500/30'
              : 'bg-gray-100 text-gray-400'
          }`}
          aria-label="Send message"
        >
          {isLoading ? (
            <LoadingSpinner />
          ) : (
            <SendIcon />
          )}
        </button>
      </div>

      {/* Helper Text */}
      <div className="flex items-center justify-between mt-2 px-1">
        <p className="text-xs text-gray-400">
          Press Enter to send
        </p>
        <p className="text-xs text-gray-400">
          Powered by RAG
        </p>
      </div>
    </form>
  )
}

/**
 * Send Icon
 */
function SendIcon() {
  return (
    <svg 
      className="w-5 h-5" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        strokeWidth={2} 
        d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
      />
    </svg>
  )
}

/**
 * Loading Spinner
 */
function LoadingSpinner() {
  return (
    <svg 
      className="w-5 h-5 animate-spin" 
      fill="none" 
      viewBox="0 0 24 24"
    >
      <circle 
        className="opacity-25" 
        cx="12" 
        cy="12" 
        r="10" 
        stroke="currentColor" 
        strokeWidth="4"
      />
      <path 
        className="opacity-75" 
        fill="currentColor" 
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )
}

export default InputBox
