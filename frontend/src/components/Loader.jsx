/**
 * Loader Component
 * Typing indicator with animated dots
 */
function Loader() {
  return (
    <div className="flex items-center gap-1 py-2">
      <div className="typing-dot w-2 h-2 bg-primary-400 rounded-full" />
      <div className="typing-dot w-2 h-2 bg-primary-400 rounded-full" />
      <div className="typing-dot w-2 h-2 bg-primary-400 rounded-full" />
      <span className="ml-2 text-sm text-gray-500">Analyzing...</span>
    </div>
  )
}

export default Loader
