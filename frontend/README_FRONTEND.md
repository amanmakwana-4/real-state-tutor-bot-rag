# Real Estate Tutor Bot - Frontend

A React-based mobile-first chat interface for the Real Estate Tutor Bot.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Fetch API** - HTTP client

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # React entry point
│   ├── api/
│   │   └── chatApi.js       # Backend API client
│   ├── components/
│   │   ├── ChatWindow.jsx   # Message display area
│   │   ├── MessageBubble.jsx # Individual message component
│   │   ├── QuickActions.jsx  # Quick action buttons
│   │   ├── InputBox.jsx      # Chat input field
│   │   └── Loader.jsx        # Loading indicator
│   ├── hooks/
│   │   └── useChat.js       # Chat state management hook
│   └── styles/
│       └── globals.css      # Tailwind + custom styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 3. Build for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

## Features

### Mobile-First Design
- Responsive layout optimized for mobile devices
- Touch-friendly buttons and inputs
- Safe area insets for notched devices
- Smooth scrolling and animations

### Chat Interface
- Real-time message display
- Auto-scroll to latest messages
- Typing indicator during response generation
- Error handling with retry options

### Score Display
- Visual score badge (0-10)
- Color-coded scoring:
  - Green (7-10): High understanding
  - Yellow (4-6): Medium understanding
  - Red (0-3): Needs improvement
- Confidence indicator

### Explanation Depth Toggle
- **Simple Mode**: Concise, beginner-friendly responses
- **Detailed Mode**: Technical, comprehensive analysis

### Quick Actions
- Pre-defined common questions
- Tap to instantly send query
- Dynamically loaded from backend

### Extracted Information Display
- Shows detected entities (location, price, area, BHK)
- Displays assumptions made by the system
- Improvement suggestions

## API Integration

The frontend communicates with the backend at `http://localhost:8000`.

### Proxy Configuration
Vite is configured to proxy `/api` requests to the backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### API Endpoints Used

- `POST /api/chat/` - Send chat message
- `GET /api/chat/quick-actions` - Get quick action buttons
- `GET /api/chat/health` - Health check

## Component Details

### ChatWindow
- Displays all messages in a scrollable container
- Shows empty state with example queries
- Handles error display

### MessageBubble
- Renders user and bot messages
- Expandable details section
- Markdown-like formatting support

### QuickActions
- Horizontal scrollable button list
- Compact and full modes
- Fallback to defaults if API unavailable

### InputBox
- Text input with character limit (500)
- Enter to send
- Loading state with spinner

### Loader
- Animated typing indicator
- Three bouncing dots

## Styling

### Custom Tailwind Classes

```css
/* Message bubbles */
.message-bubble { /* Base bubble styles */ }
.message-user { /* User message (blue, right) */ }
.message-bot { /* Bot message (white, left) */ }

/* Score badges */
.score-badge { /* Base badge */ }
.score-high { /* Green */ }
.score-medium { /* Yellow */ }
.score-low { /* Red */ }

/* Quick actions */
.quick-action-btn { /* Pill button */ }

/* Input */
.chat-input { /* Rounded input field */ }
```

### Animations
- `slide-up` - Message entry
- `fade-in` - General fade
- Typing dots bounce

## Development

### Code Style
- ESLint for linting
- Functional components with hooks
- PropTypes for type checking (optional)

### Adding New Components

1. Create component in `src/components/`
2. Follow existing patterns
3. Use Tailwind utility classes
4. Export from component file

### Modifying Styles

1. Add custom classes in `globals.css`
2. Use `@layer components` for reusable styles
3. Use `@layer utilities` for utility classes

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Troubleshooting

### "Connection Error"
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify proxy configuration

### Styles Not Loading
- Run `npm install` to ensure Tailwind is installed
- Check PostCSS configuration
- Clear browser cache

### Hot Reload Not Working
- Restart Vite dev server
- Check for file save issues
- Verify Vite configuration

## License

MIT License
