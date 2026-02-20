import { useState, useCallback, useRef } from 'react'
import { sendChatMessage } from '../api/chatApi'

/**
 * Custom hook for managing chat state and interactions
 */
export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const sessionIdRef = useRef(generateSessionId())

  /**
   * Send a message and get response
   */
  const sendMessage = useCallback(async (message, explanationDepth = 'simple') => {
    if (!message.trim()) return

    // Add user message
    const userMessage = {
      id: generateMessageId(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      // Send to API
      const response = await sendChatMessage(
        message, 
        explanationDepth,
        sessionIdRef.current
      )

      // Add bot response
      const botMessage = {
        id: generateMessageId(),
        type: 'bot',
        content: response.response,
        score: response.score,
        confidence: response.confidence,
        assumptions: response.assumptions,
        explanation: response.explanation,
        improvements: response.improvements,
        contextUsed: response.context_used,
        intentDetected: response.intent_detected,
        entitiesExtracted: response.entities_extracted,
        timestamp: new Date().toISOString(),
      }

      setMessages(prev => [...prev, botMessage])

    } catch (err) {
      console.error('Chat error:', err)
      setError(err.message || 'Failed to get response. Please try again.')
      
      // Add error message to chat
      const errorMessage = {
        id: generateMessageId(),
        type: 'bot',
        content: getErrorMessage(err),
        isError: true,
        timestamp: new Date().toISOString(),
      }
      setMessages(prev => [...prev, errorMessage])

    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setMessages([])
    sessionIdRef.current = generateSessionId()
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearError,
    clearMessages,
    sessionId: sessionIdRef.current,
  }
}

/**
 * Generate unique message ID
 */
function generateMessageId() {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Generate session ID
 */
function generateSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Get user-friendly error message
 */
function getErrorMessage(error) {
  if (error.status === 0) {
    return `🔌 **Connection Error**

Unable to reach the server. Please check:
- Is the backend running? (port 8000)
- Is your internet connection working?

Try refreshing the page or starting the backend server.`
  }

  if (error.status >= 500) {
    return `⚠️ **Server Error**

The server encountered an issue. This might be due to:
- Missing API keys (OpenAI/Gemini)
- Vector store not initialized

Please check the backend logs for details.`
  }

  return `❌ **Error**

${error.message || 'Something went wrong. Please try again.'}

If this persists, try refreshing the page.`
}

export default useChat
