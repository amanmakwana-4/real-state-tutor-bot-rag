/**
 * Chat API Module
 * Handles all communication with the backend API
 */

const API_BASE_URL = '/api'

/**
 * Custom error class for API errors
 */
class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

/**
 * Send a chat message to the backend
 * @param {string} message - User message
 * @param {string} explanationDepth - 'simple' or 'detailed'
 * @param {string} sessionId - Optional session ID
 * @returns {Promise<Object>} Chat response
 */
export async function sendChatMessage(message, explanationDepth = 'simple', sessionId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        explanation_depth: explanationDepth,
        session_id: sessionId,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        errorData.detail || 'Failed to send message',
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    throw new APIError(
      error.message || 'Network error. Please check your connection.',
      0,
      null
    )
  }
}

/**
 * Get quick action buttons from backend
 * @returns {Promise<Array>} List of quick actions
 */
export async function getQuickActions() {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/quick-actions`)
    
    if (!response.ok) {
      throw new APIError('Failed to fetch quick actions', response.status)
    }

    return await response.json()
  } catch (error) {
    console.error('Quick actions fetch error:', error)
    // Return default actions if API fails
    return getDefaultQuickActions()
  }
}

/**
 * Get health status of the backend
 * @returns {Promise<Object>} Health status
 */
export async function getHealthStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/health`)
    
    if (!response.ok) {
      throw new APIError('Health check failed', response.status)
    }

    return await response.json()
  } catch (error) {
    return {
      status: 'error',
      version: 'unknown',
      vector_store: 'unavailable',
      llm_provider: 'unavailable',
    }
  }
}

/**
 * Submit feedback for a message
 * @param {string} messageId - Message ID
 * @param {boolean} helpful - Whether the response was helpful
 * @param {string} comment - Optional comment
 * @returns {Promise<Object>} Feedback acknowledgment
 */
export async function submitFeedback(messageId, helpful, comment = '') {
  try {
    const params = new URLSearchParams({
      message_id: messageId,
      helpful: helpful.toString(),
      comment,
    })

    const response = await fetch(`${API_BASE_URL}/chat/feedback?${params}`, {
      method: 'POST',
    })

    if (!response.ok) {
      throw new APIError('Failed to submit feedback', response.status)
    }

    return await response.json()
  } catch (error) {
    console.error('Feedback submission error:', error)
    throw error
  }
}

/**
 * Default quick actions when API is unavailable
 */
function getDefaultQuickActions() {
  return [
    {
      id: 'carpet_area',
      label: 'What is carpet area?',
      query: 'What does carpet area mean?',
      icon: '📐'
    },
    {
      id: 'investment',
      label: 'Is this a good investment?',
      query: 'Is this a good investment?',
      icon: '💰'
    },
    {
      id: 'price_location',
      label: 'Price vs Location',
      query: 'Explain price vs location in Mumbai real estate',
      icon: '📍'
    },
    {
      id: 'rera',
      label: 'What is RERA?',
      query: 'What is RERA and why is it important?',
      icon: '📋'
    },
    {
      id: 'built_up',
      label: 'Built-up vs Super built-up',
      query: "What's the difference between built-up and super built-up area?",
      icon: '🏗️'
    },
    {
      id: 'price_check',
      label: 'Check property price',
      query: 'Is 1.5 Cr for 650 sq ft in Andheri a good price?',
      icon: '💵'
    }
  ]
}

export default {
  sendChatMessage,
  getQuickActions,
  getHealthStatus,
  submitFeedback,
}
