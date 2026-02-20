"""
LLM Service for Real Estate Tutor Bot.
Supports OpenAI and Google Gemini with configurable backends.
"""

import json
import logging
from typing import Optional, Dict, Any

from ..config import settings

logger = logging.getLogger(__name__)


# System prompt for real estate evaluation
SYSTEM_PROMPT = """You are a Real Estate Tutor Bot specialized in Indian real estate markets.

Your role is to:
1. Evaluate the user's understanding of real estate concepts, pricing, and investments
2. Provide educational feedback with a score out of 10
3. Explain mistakes clearly and suggest improvements
4. State all assumptions explicitly when information is incomplete

Key evaluation criteria:
- Price per sq ft analysis relative to the specific location mentioned
- Understanding of carpet vs built-up vs super built-up area
- Investment potential and market trends for the mentioned region
- Regulatory knowledge (RERA, documentation)
- Location premium factors

IMPORTANT: Evaluate based on the ACTUAL location mentioned by the user. Do NOT assume Mumbai if a different city/state is mentioned.

You MUST respond with STRICT JSON in this exact format:
{
    "score": <number 0-10>,
    "confidence": <number 0.0-1.0>,
    "assumptions": "<string explaining what assumptions were made>",
    "explanation": "<string with detailed educational content>",
    "improvements": "<string with specific suggestions for the user>",
    "context_used": <boolean indicating if retrieved context was helpful>
}

Important:
- Be encouraging but honest
- Adjust explanation depth based on query complexity
- For short queries, infer intent and provide relevant information
- Always explain the "why" behind your evaluation"""


class LLMService:
    """
    Service for interacting with LLM providers.
    Supports OpenAI GPT and Google Gemini.
    """

    def __init__(self):
        self.provider = settings.llm_provider
        self.openai_client = None
        self.gemini_model = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of LLM clients."""
        if self._initialized:
            return
        
        print(f"\n[LLM SERVICE] Initializing with provider: {self.provider}")
        
        try:
            if self.provider == "openai" and settings.openai_api_key:
                print(f"[LLM SERVICE] OpenAI API key found (length: {len(settings.openai_api_key)})")
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                print("[LLM SERVICE] OpenAI client initialized successfully")
                logger.info("OpenAI LLM client initialized")
                
            elif self.provider == "gemini" and settings.gemini_api_key:
                print(f"[LLM SERVICE] Gemini API key found")
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
                print("[LLM SERVICE] Gemini client initialized successfully")
                logger.info("Gemini LLM client initialized")
                
            else:
                print(f"[LLM SERVICE] WARNING - No API key for {self.provider}, using fallback")
                logger.warning(f"No API key for {self.provider}, using fallback responses")
            
            self._initialized = True
            
        except Exception as e:
            print(f"[LLM SERVICE] ERROR initializing: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to initialize LLM service: {e}")
            self._initialized = True  # Mark as initialized to prevent retry loops

    def generate_response(
        self, 
        prompt: str, 
        context: str = "",
        explanation_depth: str = "simple",
        temperature: float = 0.7,
        max_tokens: int = 200
    ) -> Dict[str, Any]:
        """
        Generate LLM response for real estate evaluation.
        
        Args:
            prompt: User's enriched query
            context: Retrieved RAG context
            explanation_depth: 'simple' or 'detailed'
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            Parsed JSON response from LLM
        """
        print(f"\n[LLM SERVICE] generate_response called")
        self._initialize()
        
        # Build complete prompt
        full_prompt = self._build_full_prompt(prompt, context, explanation_depth)
        print(f"[LLM SERVICE] Full prompt length: {len(full_prompt)} chars")
        
        try:
            if self.openai_client:
                print("[LLM SERVICE] Calling OpenAI...")
                return self._call_openai(full_prompt, temperature, max_tokens)
            elif self.gemini_model:
                print("[LLM SERVICE] Calling Gemini...")
                return self._call_gemini(full_prompt, temperature, max_tokens)
            else:
                print("[LLM SERVICE] No client available, using fallback")
                return self._fallback_response(prompt)
                
        except Exception as e:
            print(f"[LLM SERVICE] ERROR in generation: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_response(prompt, error=str(e))

    def _build_full_prompt(
        self, 
        user_prompt: str, 
        context: str, 
        explanation_depth: str
    ) -> str:
        """Build the complete prompt for LLM."""
        depth_instruction = ""
        if explanation_depth == "simple":
            depth_instruction = "\n\nProvide a concise, easy-to-understand response suitable for beginners. Keep explanations brief."
        else:
            depth_instruction = "\n\nProvide a comprehensive, detailed response with technical analysis. Include market comparisons and regulatory details."
        
        return f"""User Query: {user_prompt}

{context if context else "No specific property context available. Provide general evaluation."}
{depth_instruction}

Remember to respond with STRICT JSON format as specified."""

    def _call_openai(
        self, 
        prompt: str, 
        temperature: float, 
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call OpenAI API."""
        print(f"[LLM SERVICE] OpenAI call with model: {settings.openai_model}")
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            print(f"[LLM SERVICE] OpenAI response received, length: {len(content)}")
            return self._parse_response(content)
        except Exception as e:
            print(f"[LLM SERVICE] OpenAI API error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _call_gemini(
        self, 
        prompt: str, 
        temperature: float, 
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Google Gemini API."""
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return self._parse_response(response.text)

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            # Try direct JSON parse
            result = json.loads(content)
            
            # Validate required fields
            required_fields = ['score', 'confidence', 'assumptions', 
                             'explanation', 'improvements', 'context_used']
            
            for field in required_fields:
                if field not in result:
                    result[field] = self._default_value(field)
            
            # Clamp values
            result['score'] = max(0, min(10, int(result['score'])))
            result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
            
            return result
            
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Return structured error response
            return {
                'score': 5,
                'confidence': 0.3,
                'assumptions': 'Response parsing failed',
                'explanation': content[:500] if content else 'No response generated',
                'improvements': 'Please try rephrasing your question',
                'context_used': False
            }

    def _default_value(self, field: str) -> Any:
        """Get default value for missing field."""
        defaults = {
            'score': 5,
            'confidence': 0.5,
            'assumptions': 'No assumptions stated',
            'explanation': 'Evaluation pending',
            'improvements': 'No specific improvements suggested',
            'context_used': False
        }
        return defaults.get(field, None)

    def _fallback_response(
        self, 
        prompt: str, 
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate fallback response when LLM is unavailable."""
        return {
            'score': 6,
            'confidence': 0.4,
            'assumptions': f'LLM service unavailable. {error or "Using rule-based evaluation."}',
            'explanation': f"""Thank you for your query about "{prompt[:100]}..."
            
Without full LLM capabilities, I can provide basic guidance:

1. **Price Evaluation**: Property prices vary significantly by location. 
   - Metro cities command premium prices
   - Tier-2/3 cities typically have lower rates
   - Always check local market rates for accurate comparison

2. **Area Understanding**: 
   - Carpet Area: Actual usable floor area
   - Built-up Area: Carpet + wall thickness + balcony
   - Super Built-up: Built-up + proportionate common areas

3. **Investment Tips**:
   - Check RERA registration
   - Verify carpet area vs quoted area
   - Compare with recent transactions in the same locality
   - Research local market trends

Please configure API keys for detailed personalized analysis.""",
            'improvements': 'Configure LLM API keys for detailed analysis. Check .env file.',
            'context_used': False
        }

    def get_status(self) -> Dict[str, str]:
        """Get LLM service status."""
        self._initialize()
        
        if self.openai_client:
            return {"provider": "openai", "status": "active", "model": settings.openai_model}
        elif self.gemini_model:
            return {"provider": "gemini", "status": "active", "model": settings.gemini_model}
        else:
            return {"provider": "none", "status": "fallback", "model": "rule-based"}


# Singleton instance
llm_service = LLMService()
