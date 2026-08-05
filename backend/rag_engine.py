from backend.faq_knowledge import COLLEGE_KNOWLEDGE

def query_rag(query_text: str) -> str:
    """Returns strictly isolated topic information based on user keywords."""
    query_lower = query_text.lower()
    
    # Match precise topics to prevent mixing data
    if any(k in query_lower for k in ["bus", "transport", "travel", "pickup", "route", "timing"]):
        return COLLEGE_KNOWLEDGE["bus"]
    elif any(k in query_lower for k in ["hostel", "room", "curfew", "gate", "vasishta", "vedavathi"]):
        return COLLEGE_KNOWLEDGE["hostel"]
    elif any(k in query_lower for k in ["fee", "fees", "payment", "tuition", "cost"]):
        return COLLEGE_KNOWLEDGE["fee"]
    elif any(k in query_lower for k in ["college", "address", "location", "vitb", "bhimavaram", "affili"]):
        return COLLEGE_KNOWLEDGE["college"]
        
    # Default fallback if no specific keyword matches
    return "I couldn't find exact guidelines for that topic. Type **'menu'** to view the main options."