"""
Intent Detection and Entity Extraction Service.
Handles short, cryptic user inputs and intelligently infers intent.
"""

import re
from typing import Tuple, List, Optional
from ..models.schemas import Intent, ExtractedEntities, IntentAnalysis


# Keywords for intent classification
INTENT_KEYWORDS = {
    Intent.AREA_EXPLANATION: [
        "carpet", "built-up", "built up", "super built", "loading",
        "meaning", "what is", "what's", "define", "explain", "area",
        "sqft", "sq ft", "square feet", "rera"
    ],
    Intent.INVESTMENT_ANALYSIS: [
        "invest", "investment", "good buy", "worth", "buy",
        "roi", "return", "appreciate", "growth", "profit",
        "rental", "rent yield", "future", "resale"
    ],
    Intent.PRICE_EVALUATION: [
        "price", "cost", "cr", "crore", "lakh", "rate",
        "expensive", "cheap", "fair", "overpriced", "value",
        "worth", "budget", "afford", "average price"
    ],
    Intent.PROPERTY_SEARCH: [
        "find", "search", "looking for", "show me", "list",
        "available", "options", "suggest", "recommend"
    ],
    Intent.COMPARISON: [
        "compare", "vs", "versus", "better", "difference",
        "which", "or", "between"
    ]
}

# Location patterns - Mumbai specific
MUMBAI_LOCALITIES = [
    "parel", "worli", "bandra", "andheri", "powai", "goregaon",
    "malad", "borivali", "kandivali", "thane", "navi mumbai",
    "panvel", "vashi", "kharghar", "dadar", "sion", "kurla",
    "ghatkopar", "mulund", "vikhroli", "bhandup", "chembur",
    "wadala", "lower parel", "juhu", "versova", "lokhandwala",
    "santacruz", "khar", "mahim", "prabhadevi", "elphinstone",
    "mahalaxmi", "tardeo", "mira road", "bhayander", "dahisar"
]

# Indian states for location detection
INDIAN_STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
    "delhi", "mumbai", "bangalore", "chennai", "hyderabad", "kolkata", "pune"
]

# Pattern to match "place in/near City/State" or "City, State"
LOCATION_CONTEXT_PATTERN = r'(?:in|near|at)\s+([A-Za-z\s]+?)(?:,|\s+(?:' + '|'.join(INDIAN_STATES) + r'))'

# Price patterns
PRICE_PATTERNS = [
    r'(\d+(?:\.\d+)?)\s*(?:cr|crore|crores)',
    r'(\d+(?:\.\d+)?)\s*(?:l|lakh|lakhs|lac|lacs)',
    r'₹?\s*(\d+(?:\.\d+)?)\s*(?:cr|crore|l|lakh)?',
]

# Area patterns
AREA_PATTERNS = [
    r'(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square\s*feet|sft)',
    r'(\d+(?:\.\d+)?)\s*(?:sq\s*m|sqm|square\s*meters?)',
]

# BHK patterns
BHK_PATTERN = r'(\d)\s*(?:bhk|bed|bedroom|br)'


class IntentService:
    """
    Service for detecting user intent and extracting entities.
    Designed to handle very short, incomplete user inputs.
    """

    def __init__(self):
        self.locality_pattern = re.compile(
            r'\b(' + '|'.join(MUMBAI_LOCALITIES) + r')\b',
            re.IGNORECASE
        )
        self.state_pattern = re.compile(
            r'\b(' + '|'.join(INDIAN_STATES) + r')\b',
            re.IGNORECASE
        )
        # Pattern: "place in City" or "place, State" or "City, State"
        self.general_location_pattern = re.compile(
            r'(?:in|near|at)\s+([A-Za-z][A-Za-z\s]{2,20})(?:,|$|\?)|([A-Za-z][A-Za-z\s]{2,20}),\s*([A-Za-z][A-Za-z\s]+)',
            re.IGNORECASE
        )

    def detect_intent(self, user_input: str) -> Tuple[Intent, float]:
        """
        Detect the primary intent from user input.
        Returns intent and confidence score.
        """
        input_lower = user_input.lower()
        scores = {}
        
        print(f"\n[INTENT SERVICE] Detecting intent for: {user_input}")
        
        # Score each intent based on keyword matches
        for intent, keywords in INTENT_KEYWORDS.items():
            score = 0
            matched_keywords = []
            for keyword in keywords:
                if keyword in input_lower:
                    # Longer keywords get higher weight
                    score += len(keyword.split()) * 0.2
                    matched_keywords.append(keyword)
            scores[intent] = score
            if matched_keywords:
                print(f"[INTENT SERVICE] {intent}: matched {matched_keywords}, score={score}")
        
        # Special pattern matching for better accuracy
        # Price evaluation if numbers with cr/lakh present
        if re.search(r'\d+(?:\.\d+)?\s*(?:cr|crore|lakh|l)', input_lower):
            scores[Intent.PRICE_EVALUATION] = scores.get(Intent.PRICE_EVALUATION, 0) + 0.5
            print(f"[INTENT SERVICE] Price pattern matched, PRICE_EVALUATION +0.5")
        
        # Area explanation if area terms present
        if re.search(r'carpet|built.?up|loading', input_lower):
            scores[Intent.AREA_EXPLANATION] = scores.get(Intent.AREA_EXPLANATION, 0) + 0.5
            print(f"[INTENT SERVICE] Area pattern matched, AREA_EXPLANATION +0.5")
        
        # Question patterns suggest explanation intent
        if re.search(r'\?|what|how|why|meaning', input_lower):
            scores[Intent.AREA_EXPLANATION] = scores.get(Intent.AREA_EXPLANATION, 0) + 0.3
            scores[Intent.GENERAL_QUERY] = scores.get(Intent.GENERAL_QUERY, 0) + 0.2
            print(f"[INTENT SERVICE] Question pattern matched")
        
        print(f"[INTENT SERVICE] Final scores: {scores}")
        
        # Get best match
        if scores and max(scores.values()) > 0:
            best_intent = max(scores, key=scores.get)
            confidence = min(scores[best_intent] / 2.0, 0.95)
        else:
            best_intent = Intent.GENERAL_QUERY
            confidence = 0.5
        
        # Ensure minimum confidence threshold
        confidence = max(confidence, 0.4)
        
        print(f"[INTENT SERVICE] Best intent: {best_intent}, confidence: {confidence}")
        
        return best_intent, confidence

    def extract_entities(self, user_input: str) -> ExtractedEntities:
        """
        Extract entities from user input.
        Handles abbreviated and incomplete information.
        """
        input_lower = user_input.lower()
        entities = ExtractedEntities()
        
        # Extract location - try multiple patterns
        location_found = False
        
        # First try to find "City, State" pattern (e.g., "Barnagar, Madhya Pradesh")
        city_state_match = re.search(r'([A-Za-z][A-Za-z\s]{2,20}),\s*([A-Za-z][A-Za-z\s]+?)(?:\s+worth|\s+for|\s*\?|$)', user_input, re.IGNORECASE)
        if city_state_match:
            city = city_state_match.group(1).strip()
            state = city_state_match.group(2).strip()
            entities.location = f"{city.title()}, {state.title()}"
            location_found = True
        
        # Then try "in/near/at Location" pattern
        if not location_found:
            in_location_match = re.search(r'(?:in|near|at)\s+([A-Za-z][A-Za-z\s]{2,30})(?:,|\s+worth|\s+for|\s*\?|$)', user_input, re.IGNORECASE)
            if in_location_match:
                entities.location = in_location_match.group(1).strip().title()
                location_found = True
        
        # Finally try Mumbai localities
        if not location_found:
            location_match = self.locality_pattern.search(input_lower)
            if location_match:
                entities.location = location_match.group(1).title()
        
        # Extract price
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, input_lower)
            if match:
                value = float(match.group(1))
                if 'cr' in input_lower or 'crore' in input_lower:
                    entities.price = value
                    entities.price_unit = 'Cr'
                elif 'l' in input_lower or 'lakh' in input_lower:
                    entities.price = value
                    entities.price_unit = 'Lakh'
                else:
                    # Infer unit based on value magnitude
                    if value > 100:
                        entities.price = value
                        entities.price_unit = 'Lakh'
                    else:
                        entities.price = value
                        entities.price_unit = 'Cr'
                break
        
        # Extract area
        for pattern in AREA_PATTERNS:
            match = re.search(pattern, input_lower)
            if match:
                entities.area = float(match.group(1))
                if 'sq m' in input_lower or 'sqm' in input_lower:
                    entities.area_unit = 'sq m'
                else:
                    entities.area_unit = 'sq ft'
                break
        
        # Extract BHK
        bhk_match = re.search(BHK_PATTERN, input_lower)
        if bhk_match:
            entities.bhk = int(bhk_match.group(1))
        
        # Extract property type keywords
        property_types = ['flat', 'apartment', 'villa', 'plot', 'house', 'penthouse', 'studio']
        for ptype in property_types:
            if ptype in input_lower:
                entities.property_type = ptype.title()
                break
        
        # Extract keywords for semantic search
        entities.keywords = self._extract_keywords(user_input)
        
        return entities

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords for search."""
        # Remove common words and extract significant terms
        stop_words = {
            'is', 'the', 'a', 'an', 'in', 'for', 'of', 'to', 'this',
            'that', 'it', 'with', 'and', 'or', 'but', 'so', 'if',
            'my', 'me', 'i', 'you', 'what', 'how', 'why', 'when'
        }
        
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        
        return list(set(keywords))[:10]

    def enrich_query(
        self, 
        user_input: str, 
        intent: Intent, 
        entities: ExtractedEntities
    ) -> Tuple[str, List[str]]:
        """
        Enrich the user query with inferred context.
        Returns enriched query and list of assumptions made.
        """
        assumptions = []
        enriched_parts = [user_input]
        
        # Infer missing details based on intent and available entities
        if intent == Intent.PRICE_EVALUATION:
            if entities.price and entities.location:
                if not entities.bhk:
                    # Infer BHK from price range
                    if entities.price_unit == 'Cr':
                        if entities.price < 1:
                            entities.bhk = 1
                            assumptions.append("Assumed 1 BHK based on sub-1 Cr price range")
                        elif entities.price < 2:
                            entities.bhk = 2
                            assumptions.append("Assumed 2 BHK based on 1-2 Cr price range")
                        else:
                            entities.bhk = 3
                            assumptions.append("Assumed 3 BHK based on 2+ Cr price range")
                
                if not entities.area:
                    # Infer area from BHK
                    bhk_area_map = {1: 450, 2: 700, 3: 1000, 4: 1400}
                    entities.area = bhk_area_map.get(entities.bhk or 2, 700)
                    entities.area_unit = 'sq ft'
                    assumptions.append(f"Assumed ~{entities.area} sq ft carpet area for {entities.bhk or 2} BHK")
        
        # Build enriched query
        context_parts = []
        
        if entities.location:
            context_parts.append(f"Location: {entities.location}")
        
        if entities.price:
            context_parts.append(f"Price: {entities.price} {entities.price_unit or 'Cr'}")
        
        if entities.area:
            context_parts.append(f"Area: {entities.area} {entities.area_unit or 'sq ft'}")
        
        if entities.bhk:
            context_parts.append(f"Configuration: {entities.bhk} BHK")
        
        if entities.property_type:
            context_parts.append(f"Type: {entities.property_type}")
        
        if context_parts:
            enriched_parts.append(f"\n[Extracted Context: {', '.join(context_parts)}]")
        
        enriched_query = ' '.join(enriched_parts)
        
        return enriched_query, assumptions

    def analyze(self, user_input: str) -> IntentAnalysis:
        """
        Complete analysis pipeline: detect intent, extract entities, enrich query.
        """
        # Step 1: Detect intent
        intent, confidence = self.detect_intent(user_input)
        
        # Step 2: Extract entities
        entities = self.extract_entities(user_input)
        
        # Step 3: Enrich query
        enriched_query, assumptions = self.enrich_query(user_input, intent, entities)
        
        return IntentAnalysis(
            intent=intent,
            confidence=confidence,
            entities=entities,
            enriched_query=enriched_query,
            assumptions=assumptions
        )


# Singleton instance
intent_service = IntentService()
