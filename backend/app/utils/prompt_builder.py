"""
Prompt Builder Utility.
Constructs optimized prompts for different query types.
"""

from typing import List, Optional
from ..models.schemas import Intent, IntentAnalysis, RetrievedContext


class PromptBuilder:
    """
    Utility class for building targeted prompts based on intent.
    Optimizes prompts for better LLM responses.
    """

    # Intent-specific prompt templates
    INTENT_TEMPLATES = {
        Intent.PRICE_EVALUATION: """
Evaluate this property price query. Consider:
- Price per square foot compared to locality average
- Premium factors (amenities, floor, view)
- Market trends in the area
- RERA compliance impact on pricing
- Comparison with recent transactions

User Query: {query}

{context}

Provide a score based on:
- Understanding of local market rates (3 points)
- Area calculation accuracy (2 points)
- Investment timing awareness (2 points)
- Documentation knowledge (2 points)
- Negotiation readiness (1 point)
""",
        
        Intent.AREA_EXPLANATION: """
Explain real estate area concepts clearly. Cover:
- Carpet Area: Actual floor area within walls
- Built-up Area: Carpet + wall thickness + balcony
- Super Built-up Area: Built-up + share of common areas
- Loading Factor: Percentage difference from carpet to super built-up
- RERA requirements for area disclosure

User Query: {query}

{context}

Score based on understanding of:
- Technical definitions (3 points)
- RERA regulations (2 points)
- Practical implications (3 points)
- Calculation methods (2 points)
""",
        
        Intent.INVESTMENT_ANALYSIS: """
Analyze this real estate investment query. Consider:
- Location appreciation potential
- Rental yield expectations
- Infrastructure development impact
- Market cycle timing
- Liquidity and exit options
- Tax implications

User Query: {query}

{context}

Score based on:
- Location analysis (2 points)
- Financial understanding (3 points)
- Risk awareness (2 points)
- Due diligence knowledge (2 points)
- Market timing (1 point)
""",
        
        Intent.PROPERTY_SEARCH: """
Help with this property search query. Consider:
- Budget alignment with location
- Configuration vs family needs
- Connectivity and infrastructure
- Future appreciation potential
- Available inventory

User Query: {query}

{context}

Provide relevant property suggestions with scoring based on match quality.
""",
        
        Intent.COMPARISON: """
Compare real estate options objectively. Consider:
- Price per sq ft difference
- Location advantages/disadvantages
- Builder reputation
- Amenities comparison
- Appreciation potential

User Query: {query}

{context}

Score comparison understanding out of 10.
""",
        
        Intent.GENERAL_QUERY: """
Answer this real estate query helpfully. Provide:
- Clear, accurate information
- Relevant examples from Mumbai market
- Actionable advice
- Important considerations

User Query: {query}

{context}

Score understanding and provide educational guidance.
"""
    }

    @classmethod
    def build_prompt(
        cls,
        analysis: IntentAnalysis,
        contexts: List[RetrievedContext],
        explanation_depth: str = "simple"
    ) -> str:
        """
        Build a complete prompt for LLM evaluation.
        
        Args:
            analysis: Intent analysis with entities
            contexts: Retrieved context documents
            explanation_depth: simple or detailed
            
        Returns:
            Complete prompt string
        """
        # Get template for intent
        template = cls.INTENT_TEMPLATES.get(
            analysis.intent, 
            cls.INTENT_TEMPLATES[Intent.GENERAL_QUERY]
        )
        
        # Format context
        context_str = cls._format_contexts(contexts)
        
        # Add assumptions if any
        assumptions_str = ""
        if analysis.assumptions:
            assumptions_str = "\n\n**Note:** " + "; ".join(analysis.assumptions)
        
        # Add depth instruction
        depth_str = cls._get_depth_instruction(explanation_depth)
        
        # Build final prompt
        prompt = template.format(
            query=analysis.enriched_query,
            context=context_str
        )
        
        return prompt + assumptions_str + depth_str

    @classmethod
    def _format_contexts(cls, contexts: List[RetrievedContext]) -> str:
        """Format retrieved contexts for prompt."""
        if not contexts:
            return "**Market Context:** No specific property data available. Provide general evaluation based on Mumbai market knowledge."
        
        parts = ["**Relevant Property Data:**"]
        
        for i, ctx in enumerate(contexts, 1):
            parts.append(f"\n[Property {i}] (Relevance: {ctx.score:.0%})")
            parts.append(ctx.content)
            
            # Add key metadata
            if ctx.metadata:
                key_info = []
                for key in ['location', 'price', 'carpet_area', 'bhk']:
                    if key in ctx.metadata:
                        key_info.append(f"{key}: {ctx.metadata[key]}")
                if key_info:
                    parts.append(f"Key Info: {', '.join(key_info)}")
        
        return "\n".join(parts)

    @classmethod
    def _get_depth_instruction(cls, depth: str) -> str:
        """Get instruction for explanation depth."""
        if depth == "simple":
            return """

**Response Format:** Keep explanation concise and beginner-friendly. 
- Use simple language
- Maximum 150 words for explanation
- 1-2 key improvement suggestions"""
        else:
            return """

**Response Format:** Provide comprehensive analysis.
- Include technical details
- Reference market data
- Explain regulatory aspects
- Provide multiple improvement points
- Include relevant calculations if applicable"""

    @classmethod
    def build_search_query(cls, analysis: IntentAnalysis) -> str:
        """
        Build an optimized search query for vector retrieval.
        """
        parts = []
        entities = analysis.entities
        
        # Intent-based keywords
        intent_keywords = {
            Intent.PRICE_EVALUATION: ["price", "valuation", "rate", "cost"],
            Intent.AREA_EXPLANATION: ["carpet area", "built-up", "measurement"],
            Intent.INVESTMENT_ANALYSIS: ["investment", "appreciation", "ROI", "rental"],
            Intent.PROPERTY_SEARCH: ["property", "available", "listing"],
            Intent.COMPARISON: ["compare", "versus", "difference"],
        }
        
        # Add intent keywords
        keywords = intent_keywords.get(analysis.intent, [])
        parts.extend(keywords[:2])
        
        # Add entity information
        if entities.location:
            parts.append(entities.location)
        
        if entities.bhk:
            parts.append(f"{entities.bhk}bhk")
        
        if entities.price:
            parts.append(f"{entities.price}{entities.price_unit or 'cr'}")
        
        if entities.area:
            parts.append(f"{entities.area}sqft")
        
        # Add extracted keywords
        parts.extend(entities.keywords[:3])
        
        return " ".join(parts)


# Export utility functions
def build_prompt(analysis: IntentAnalysis, contexts: List[RetrievedContext], depth: str = "simple") -> str:
    return PromptBuilder.build_prompt(analysis, contexts, depth)

def build_search_query(analysis: IntentAnalysis) -> str:
    return PromptBuilder.build_search_query(analysis)
