import { useState, useCallback } from 'react'
import ChatWindow from './components/ChatWindow'
import QuickActions from './components/QuickActions'
import InputBox from './components/InputBox'
import { useChat } from './hooks/useChat'

/**
 * Main Application Component
 * Real Estate Tutor Bot - Smart RAG Evaluation Platform
 */
function App() {
  // Explanation depth toggle: 'simple' or 'detailed'
  const [explanationDepth, setExplanationDepth] = useState('simple')
  
  // Chat hook for message management
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearError,
    clearMessages
  } = useChat()

  // Handle sending a message
  const handleSendMessage = useCallback((message) => {
    sendMessage(message, explanationDepth)
  }, [sendMessage, explanationDepth])

  // Handle quick action click
  const handleQuickAction = useCallback((query) => {
    handleSendMessage(query)
  }, [handleSendMessage])

  // Toggle explanation depth
  const toggleExplanationDepth = useCallback(() => {
    setExplanationDepth(prev => prev === 'simple' ? 'detailed' : 'simple')
  }, [])

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between pt-safe">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
            <span className="text-xl">🏠</span>
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">Real Estate Tutor</h1>
            <p className="text-xs text-gray-500">Smart Learning Platform</p>
          </div>
        </div>
        
        {/* Explanation Depth Toggle */}
        <div className="flex items-center gap-2">
          <span className={`text-xs ${explanationDepth === 'simple' ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>
            Simple
          </span>
          <button
            onClick={toggleExplanationDepth}
            className={`toggle-switch ${explanationDepth === 'detailed' ? 'toggle-switch-enabled' : 'toggle-switch-disabled'}`}
            aria-label="Toggle explanation depth"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform duration-200 ${
                explanationDepth === 'detailed' ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
          <span className={`text-xs ${explanationDepth === 'detailed' ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>
            Detailed
          </span>
        </div>
      </header>

      {/* Quick Actions - Only show when no messages or at start */}
      {messages.length === 0 && (
        <QuickActions onActionClick={handleQuickAction} />
      )}

      {/* Chat Window */}
      <ChatWindow 
        messages={messages} 
        isLoading={isLoading}
        error={error}
        onClearError={clearError}
      />

      {/* Quick Actions - Compact version when there are messages */}
      {messages.length > 0 && (
        <div className="px-4 py-2 bg-white border-t border-gray-100">
          <QuickActions 
            onActionClick={handleQuickAction} 
            compact={true}
          />
        </div>
      )}

      {/* Input Box */}
      <InputBox 
        onSend={handleSendMessage} 
        isLoading={isLoading}
        placeholder={messages.length === 0 
          ? "Try: '700 sq ft Parel worth 2.1 Cr?'" 
          : "Type your question..."
        }
      />
    </div>
  )
}

export default App
