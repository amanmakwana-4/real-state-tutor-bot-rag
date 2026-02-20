import { useState, useEffect } from 'react'
import { getQuickActions } from '../api/chatApi'

/**
 * Quick Actions Component
 * Displays tappable buttons for common queries
 */
function QuickActions({ onActionClick, compact = false }) {
  const [actions, setActions] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  // Load quick actions from API
  useEffect(() => {
    loadActions()
  }, [])

  const loadActions = async () => {
    try {
      const data = await getQuickActions()
      setActions(data)
    } catch (error) {
      console.error('Failed to load quick actions:', error)
      // Use default actions
      setActions(getDefaultActions())
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className={`${compact ? 'py-1' : 'px-4 py-6'}`}>
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          {[1, 2, 3].map(i => (
            <div 
              key={i}
              className="h-10 w-32 bg-gray-100 rounded-full animate-pulse shrink-0"
            />
          ))}
        </div>
      </div>
    )
  }

  // Compact mode - horizontal scroll only
  if (compact) {
    return (
      <div className="flex gap-2 overflow-x-auto scrollbar-hide">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onActionClick(action.query)}
            className="quick-action-btn shrink-0 flex items-center gap-2"
          >
            <span>{action.icon}</span>
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    )
  }

  // Full mode - with header
  return (
    <div className="px-4 py-6 bg-white border-b border-gray-100">
      <h3 className="text-sm font-medium text-gray-500 mb-3">
        Quick Questions
      </h3>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onActionClick(action.query)}
            className="quick-action-btn flex items-center gap-2"
          >
            <span>{action.icon}</span>
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

/**
 * Default quick actions fallback
 */
function getDefaultActions() {
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

export default QuickActions
