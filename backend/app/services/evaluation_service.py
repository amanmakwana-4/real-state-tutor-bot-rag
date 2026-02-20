"""
Evaluation Service - Main Orchestrator.
Combines intent detection, RAG retrieval, and LLM evaluation.
"""

import logging
import traceback
from typing import Optional

from ..models.schemas import (
    ChatRequest, 
    ChatResponse, 
    LLMEvaluation,
    ExplanationDepth
)
from .intent_service import intent_service
from .rag_service import rag_service
from .llm_service import llm_service

logger = logging.getLogger(__name__)

# Enable console output for debugging
import sys
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


class EvaluationService:
    """
    Main orchestrator service that combines all processing steps.
    Handles the complete pipeline from user input to evaluated response.
    """

    def __init__(self):
        self.intent_service = intent_service
        self.rag_service = rag_service
        self.llm_service = llm_service

    async def process_query(self, request: ChatRequest) -> ChatResponse:
        """
        Process a user query through the complete evaluation pipeline.
        
        Pipeline:
        1. Intent Detection & Entity Extraction
        2. Query Enrichment
        3. RAG Context Retrieval
        4. LLM Evaluation
        5. Response Formatting
        
        Args:
            request: Incoming chat request
            
        Returns:
            Complete chat response with evaluation
        """
        print(f"\n{'='*50}")
        print(f"[EVALUATION SERVICE] Processing query: {request.message}")
        print(f"{'='*50}")
        
        try:
            # Step 1 & 2: Analyze intent and extract entities
            print("\n[STEP 1] Intent Detection...")
            try:
                analysis = self.intent_service.analyze(request.message)
                print(f"[STEP 1] SUCCESS - Intent: {analysis.intent}, Confidence: {analysis.confidence}")
                print(f"[STEP 1] Entities: {analysis.entities}")
                print(f"[STEP 1] Enriched Query: {analysis.enriched_query[:100]}...")
            except Exception as e:
                print(f"[STEP 1] ERROR in Intent Service: {str(e)}")
                traceback.print_exc()
                raise
            
            # Step 3: Build search query and retrieve context
            print("\n[STEP 2] RAG Context Retrieval...")
            try:
                search_query = self.rag_service.build_search_query(analysis)
                print(f"[STEP 2] Search Query: {search_query}")
                retrieved_contexts = self.rag_service.retrieve(
                    query=search_query,
                    analysis=analysis
                )
                print(f"[STEP 2] SUCCESS - Retrieved {len(retrieved_contexts)} contexts")
            except Exception as e:
                print(f"[STEP 2] ERROR in RAG Service: {str(e)}")
                traceback.print_exc()
                retrieved_contexts = []
            
            # Format context for prompt
            context_text = self.rag_service.format_context_for_prompt(retrieved_contexts)
            print(f"[STEP 2] Context formatted, length: {len(context_text)} chars")
            
            # Step 4: Generate LLM evaluation
            print("\n[STEP 3] LLM Evaluation...")
            try:
                llm_response = self.llm_service.generate_response(
                    prompt=analysis.enriched_query,
                    context=context_text,
                    explanation_depth=request.explanation_depth.value
                )
                print(f"[STEP 3] SUCCESS - LLM Response received")
                print(f"[STEP 3] Score: {llm_response.get('score')}, Confidence: {llm_response.get('confidence')}")
            except Exception as e:
                print(f"[STEP 3] ERROR in LLM Service: {str(e)}")
                traceback.print_exc()
                raise
            
            # Step 5: Build response
            print("\n[STEP 4] Building Response...")
            response = self._build_response(
                analysis=analysis,
                llm_response=llm_response,
                retrieved_contexts=retrieved_contexts,
                explanation_depth=request.explanation_depth
            )
            
            print(f"[STEP 4] SUCCESS - Response built")
            print(f"{'='*50}\n")
            return response
            
        except Exception as e:
            print(f"\n[ERROR] Query processing failed: {str(e)}")
            traceback.print_exc()
            logger.error(f"Query processing failed: {e}")
            return self._build_error_response(request.message, str(e))

    def _build_response(
        self,
        analysis,
        llm_response: dict,
        retrieved_contexts: list,
        explanation_depth: ExplanationDepth
    ) -> ChatResponse:
        """Build the final chat response."""
        
        # Format the response text based on depth preference
        if explanation_depth == ExplanationDepth.SIMPLE:
            response_text = self._format_simple_response(llm_response)
        else:
            response_text = self._format_detailed_response(llm_response, analysis)
        
        return ChatResponse(
            response=response_text,
            score=llm_response.get('score'),
            confidence=llm_response.get('confidence'),
            assumptions=llm_response.get('assumptions'),
            explanation=llm_response.get('explanation'),
            improvements=llm_response.get('improvements'),
            context_used=llm_response.get('context_used', len(retrieved_contexts) > 0),
            intent_detected=analysis.intent,
            entities_extracted=analysis.entities,
            retrieved_contexts=retrieved_contexts
        )

    def _format_simple_response(self, llm_response: dict) -> str:
        """Format a concise response for simple mode."""
        parts = []
        
        # Score summary
        score = llm_response.get('score', 5)
        parts.append(f"📊 **Score: {score}/10**")
        
        # Brief explanation
        explanation = llm_response.get('explanation', '')
        if explanation:
            # Truncate for simple mode
            if len(explanation) > 300:
                explanation = explanation[:300] + "..."
            parts.append(f"\n{explanation}")
        
        # Quick improvement tip
        improvements = llm_response.get('improvements', '')
        if improvements:
            # Just first sentence for simple mode
            first_sentence = improvements.split('.')[0] + '.'
            parts.append(f"\n💡 **Tip:** {first_sentence}")
        
        return '\n'.join(parts)

    def _format_detailed_response(self, llm_response: dict, analysis) -> str:
        """Format a comprehensive response for detailed mode."""
        parts = []
        
        # Score with confidence
        score = llm_response.get('score', 5)
        confidence = llm_response.get('confidence', 0.5)
        confidence_label = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
        
        parts.append(f"📊 **Evaluation Score: {score}/10** (Confidence: {confidence_label})")
        
        # Assumptions made
        assumptions = llm_response.get('assumptions', '')
        if assumptions:
            parts.append(f"\n📝 **Assumptions Made:**\n{assumptions}")
        
        # Detected entities summary
        if analysis and analysis.entities:
            entities = analysis.entities
            entity_parts = []
            if entities.location:
                entity_parts.append(f"Location: {entities.location}")
            if entities.price:
                entity_parts.append(f"Price: {entities.price} {entities.price_unit or 'Cr'}")
            if entities.area:
                entity_parts.append(f"Area: {entities.area} {entities.area_unit or 'sq ft'}")
            if entities.bhk:
                entity_parts.append(f"BHK: {entities.bhk}")
            
            if entity_parts:
                parts.append(f"\n🔍 **Extracted Details:** {' | '.join(entity_parts)}")
        
        # Full explanation
        explanation = llm_response.get('explanation', '')
        if explanation:
            parts.append(f"\n📖 **Analysis:**\n{explanation}")
        
        # Improvements
        improvements = llm_response.get('improvements', '')
        if improvements:
            parts.append(f"\n💡 **Suggestions for Improvement:**\n{improvements}")
        
        # Context indicator
        if llm_response.get('context_used'):
            parts.append("\n✅ *Analysis based on real property data*")
        
        return '\n'.join(parts)

    def _build_error_response(self, original_message: str, error: str) -> ChatResponse:
        """Build an error response when processing fails."""
        from ..models.schemas import Intent, ExtractedEntities
        
        return ChatResponse(
            response=f"""I apologize, but I encountered an issue processing your query.

**Your question:** "{original_message[:100]}..."

**What you can try:**
1. Rephrase your question with more details
2. Try a quick action button for common queries
3. Check if the backend services are running

*Technical details: {error[:200]}*""",
            score=None,
            confidence=None,
            assumptions="Processing error occurred",
            explanation="Unable to complete evaluation",
            improvements="Please try again or rephrase your query",
            context_used=False,
            intent_detected=Intent.GENERAL_QUERY,
            entities_extracted=ExtractedEntities(),
            retrieved_contexts=[]
        )

    def get_quick_actions(self) -> list:
        """Get predefined quick action buttons."""
        return [
            {
                "id": "carpet_area",
                "label": "What is carpet area?",
                "query": "What does carpet area mean?",
                "icon": "📐"
            },
            {
                "id": "investment",
                "label": "Is this a good investment?",
                "query": "Is this a good investment?",
                "icon": "💰"
            },
            {
                "id": "price_location",
                "label": "Price vs Location",
                "query": "Explain price vs location in Mumbai real estate",
                "icon": "📍"
            },
            {
                "id": "rera",
                "label": "What is RERA?",
                "query": "What is RERA and why is it important?",
                "icon": "📋"
            },
            {
                "id": "built_up",
                "label": "Built-up vs Super built-up",
                "query": "What's the difference between built-up and super built-up area?",
                "icon": "🏗️"
            },
            {
                "id": "price_check",
                "label": "Check property price",
                "query": "Is 1.5 Cr for 650 sq ft in Andheri a good price?",
                "icon": "💵"
            }
        ]


# Singleton instance
evaluation_service = EvaluationService()
