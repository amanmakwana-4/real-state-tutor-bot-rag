"""
Test script to debug the Real Estate Tutor Bot pipeline.
Run with: python test_pipeline.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("Testing Real Estate Tutor Bot Pipeline")
print("=" * 60)

# Test 1: Check environment variables
print("\n[TEST 1] Checking environment variables...")
from app.config import settings
print(f"  LLM Provider: {settings.llm_provider}")
print(f"  OpenAI Key: {'SET' if settings.openai_api_key else 'NOT SET'}")
print(f"  Gemini Key: {'SET' if settings.gemini_api_key else 'NOT SET'}")
print(f"  Use Pinecone: {settings.use_pinecone}")
print(f"  Pinecone Key: {'SET' if settings.pinecone_api_key else 'NOT SET'}")
print(f"  Pinecone Host: {settings.pinecone_host}")

# Test 2: Test Intent Service
print("\n[TEST 2] Testing Intent Service...")
try:
    from app.services.intent_service import intent_service
    test_input = "700 sq ft Parel worth 2.1 Cr?"
    print(f"  Input: {test_input}")
    
    analysis = intent_service.analyze(test_input)
    print(f"  Intent: {analysis.intent} (value: {analysis.intent.value})")
    print(f"  Confidence: {analysis.confidence}")
    print(f"  Entities: {analysis.entities}")
    print(f"  Enriched Query: {analysis.enriched_query[:100]}...")
    print("  [SUCCESS] Intent Service OK")
except Exception as e:
    print(f"  [ERROR] Intent Service failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test Embedding Service
print("\n[TEST 3] Testing Embedding Service...")
try:
    from app.services.embedding_service import embedding_service
    test_text = "2 BHK flat in Parel Mumbai"
    
    embedding = embedding_service.embed_query(test_text)
    if embedding is None:
        print("  [WARNING] Embedding returned None - API key might not be set")
    else:
        print(f"  Embedding dimension: {len(embedding)}")
        print("  [SUCCESS] Embedding Service OK")
except Exception as e:
    print(f"  [ERROR] Embedding Service failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test RAG Service
print("\n[TEST 4] Testing RAG Service...")
try:
    from app.services.rag_service import rag_service
    from app.services.intent_service import intent_service
    
    analysis = intent_service.analyze("property in Parel")
    search_query = rag_service.build_search_query(analysis)
    print(f"  Search query: {search_query}")
    
    contexts = rag_service.retrieve(search_query, analysis)
    print(f"  Retrieved {len(contexts)} contexts")
    if contexts:
        print(f"  First context score: {contexts[0].score}")
    print("  [SUCCESS] RAG Service OK")
except Exception as e:
    print(f"  [ERROR] RAG Service failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test LLM Service
print("\n[TEST 5] Testing LLM Service...")
try:
    from app.services.llm_service import llm_service
    
    test_prompt = "Is 2.1 Cr for 700 sq ft in Parel a good price?"
    test_context = "Average price in Parel is 30,000/sq ft. A 700 sq ft property would be around 2.1 Cr."
    
    response = llm_service.generate_response(
        prompt=test_prompt,
        context=test_context,
        explanation_depth="simple"
    )
    print(f"  Response keys: {list(response.keys())}")
    print(f"  Score: {response.get('score')}")
    print(f"  Confidence: {response.get('confidence')}")
    print("  [SUCCESS] LLM Service OK")
except Exception as e:
    print(f"  [ERROR] LLM Service failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Full Pipeline Test
print("\n[TEST 6] Testing Full Pipeline...")
try:
    from app.services.evaluation_service import evaluation_service
    from app.models.schemas import ChatRequest, ExplanationDepth
    import asyncio
    
    request = ChatRequest(
        message="700 sq ft Parel worth 2.1 Cr?",
        explanation_depth=ExplanationDepth.SIMPLE
    )
    
    # Run async function
    async def test_pipeline():
        return await evaluation_service.process_query(request)
    
    response = asyncio.run(test_pipeline())
    print(f"  Response type: {type(response)}")
    print(f"  Intent detected: {response.intent_detected}")
    print(f"  Score: {response.score}")
    print(f"  Contexts retrieved: {len(response.retrieved_contexts)}")
    print("  [SUCCESS] Full Pipeline OK")
except Exception as e:
    print(f"  [ERROR] Full Pipeline failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Testing Complete")
print("=" * 60)
