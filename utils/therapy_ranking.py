import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

def rank_therapies(therapies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank therapy recommendations based on scores
    
    Args:
        therapies: List of therapy recommendations
        
    Returns:
        Ranked list of therapy recommendations
    """
    logger.debug(f"Ranking {len(therapies)} therapies")
    
    if not therapies:
        return []
    
    # Calculate overall score if not already present
    for therapy in therapies:
        if 'overall_score' not in therapy:
            # Calculate weighted average of scores
            scores = [
                therapy.get('efficacy_score', 0) * 0.35,
                therapy.get('compatibility_score', 0) * 0.25,
                therapy.get('safety_score', 0) * 0.25,
                therapy.get('cost_score', 0) * 0.15
            ]
            therapy['overall_score'] = sum(scores)
    
    # Sort therapies by overall score (descending)
    ranked_therapies = sorted(
        therapies, 
        key=lambda x: x.get('overall_score', 0), 
        reverse=True
    )
    
    logger.debug(f"Therapies ranked successfully. Top score: {ranked_therapies[0].get('overall_score', 0) if ranked_therapies else 'N/A'}")
    return ranked_therapies
