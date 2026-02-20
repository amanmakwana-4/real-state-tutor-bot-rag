# Real Estate Tutor Bot - Backend

A FastAPI-based backend for the Real Estate Tutor Bot - Smart RAG Evaluation Platform.

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── routes/
│   │   └── chat.py          # Chat API endpoints
│   ├── services/
│   │   ├── intent_service.py    # Intent detection & entity extraction
│   │   ├── llm_service.py       # LLM integration (OpenAI/Gemini)
│   │   ├── embedding_service.py # Text embeddings
│   │   ├── rag_service.py       # RAG orchestration
│   │   └── evaluation_service.py # Main pipeline orchestrator
│   ├── vector_store/
│   │   ├── faiss_store.py   # Local FAISS vector store
│   │   └── pinecone_store.py # Cloud Pinecone vector store
│   ├── models/
│   │   └── schemas.py       # Pydantic data models
│   └── utils/
│       └── prompt_builder.py # Prompt engineering utilities
├── data/
│   └── property_listings.csv # Sample property data
├── scripts/
│   └── build_faiss_index.py # Index builder script
├── requirements.txt
└── .env.example
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
copy .env.example .env
# Edit .env with your API keys
```

Required API keys:
- `OPENAI_API_KEY` - For GPT models and embeddings
- OR `GEMINI_API_KEY` - For Google Gemini
- `PINECONE_API_KEY` (optional) - For cloud vector store

### 4. Build FAISS Index

```bash
python scripts/build_faiss_index.py
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/chat/
Process a chat message and return evaluation.

**Request:**
```json
{
  "message": "700 sq ft Parel worth 2.1 Cr?",
  "explanation_depth": "simple",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Detailed evaluation text...",
  "score": 7,
  "confidence": 0.85,
  "assumptions": "Assumed 2 BHK based on area",
  "explanation": "Full explanation...",
  "improvements": "Suggestions...",
  "context_used": true,
  "intent_detected": "PRICE_EVALUATION",
  "entities_extracted": {
    "location": "Parel",
    "price": 2.1,
    "price_unit": "Cr",
    "area": 700,
    "area_unit": "sq ft"
  },
  "retrieved_contexts": []
}
```

### GET /api/chat/quick-actions
Get predefined quick action buttons.

### GET /api/chat/health
Health check with service status.

### GET /api/chat/stats
System statistics.

## Input Intelligence Pipeline

The system handles short, incomplete inputs through:

1. **Intent Detection** - Classifies queries into:
   - `AREA_EXPLANATION` - Questions about carpet/built-up area
   - `INVESTMENT_ANALYSIS` - Investment-related queries
   - `PRICE_EVALUATION` - Property valuation questions
   - `PROPERTY_SEARCH` - Property lookup requests
   - `COMPARISON` - Comparison queries
   - `GENERAL_QUERY` - Other questions

2. **Entity Extraction** - Extracts:
   - Location (Mumbai localities)
   - Price (with unit inference)
   - Area (sq ft/sq m)
   - BHK configuration
   - Property type

3. **Query Enrichment** - Fills missing details:
   - Infers BHK from price range
   - Infers area from BHK
   - Adds assumptions explicitly

4. **RAG Retrieval** - Finds relevant context:
   - Builds optimized search query
   - Retrieves top-k matches
   - Filters by similarity threshold

5. **LLM Evaluation** - Generates response:
   - Uses structured system prompt
   - Returns JSON with score
   - Explains assumptions

## Vector Store Configuration

### FAISS (Default)
- Local storage in `data/faiss_index/`
- No API key required
- Good for development/testing

### Pinecone (Cloud)
- Set `USE_PINECONE=true` in `.env`
- Requires `PINECONE_API_KEY`
- Better for production

## LLM Configuration

### OpenAI (Default)
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

### Google Gemini
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## Troubleshooting

### "FAISS index empty"
Run `python scripts/build_faiss_index.py` to build the index.

### "LLM service unavailable"
Check API keys in `.env` file.

### "Rate limit exceeded"
Reduce request frequency or upgrade API plan.

## License

MIT License
