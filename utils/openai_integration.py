import os
import json
import logging
from typing import Dict, Any, List

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_therapy_recommendations(
    agent_type: str,
    profile: Dict[str, Any],
    entities: Dict[str, Any],
    query: str
) -> List[Dict[str, Any]]:
    """
    Get therapy recommendations from OpenAI based on agent type
    
    Args:
        agent_type: The type of agent (allopathy, homeopathy, or both)
        profile: User profile data
        entities: Extracted entities from pathology report
        query: User query
        
    Returns:
        List of therapy recommendations
    """
    logger.debug(f"Getting therapy recommendations for agent type: {agent_type}")
    
    # Handle empty API key
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not provided. Using mock data.")
        return _get_mock_recommendations(agent_type)
    
    # Create system prompt based on agent type
    if agent_type == "allopathy":
        system_prompt = _get_allopathy_system_prompt()
    elif agent_type == "homeopathy":
        system_prompt = _get_homeopathy_system_prompt()
    else:  # both
        system_prompt = _get_combined_system_prompt()
        
    # Prepare user data for the prompt
    user_data = {
        "profile": profile,
        "entities": entities,
        "query": query
    }
    
    # Serialize data for the prompt
    user_data_json = json.dumps(user_data, indent=2)
    
    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the user data:\n{user_data_json}\n\nPlease provide therapy recommendations."}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        # Parse response
        recommendations = json.loads(response.choices[0].message.content)
        
        # Ensure we have the therapies field
        if "therapies" not in recommendations:
            logger.error("Invalid response format from OpenAI: missing 'therapies' field")
            return []
        
        return recommendations["therapies"]
    except Exception as e:
        logger.error(f"Error getting recommendations from OpenAI: {str(e)}")
        raise

def _get_allopathy_system_prompt() -> str:
    """Get system prompt for allopathy agent"""
    return """
    You are a specialized medical AI trained to provide allopathic therapy recommendations.
    
    Use evidence-based medical knowledge from PubMed, Clinical Trials, FDA, and WHO data.
    
    For each therapy recommendation, provide:
    1. Therapy name
    2. Description
    3. Efficacy score (0-100)
    4. Compatibility score based on patient profile (0-100)
    5. Safety score (0-100)
    6. Cost score (higher = more affordable, 0-100)
    7. Side effects
    8. Contraindications
    9. Supporting evidence (citations or research basis)
    
    Your response must be well-structured and in JSON format with a 'therapies' array.
    
    Response format example:
    {
      "therapies": [
        {
          "therapy_type": "allopathy",
          "therapy_name": "Therapy Name",
          "description": "Detailed description",
          "efficacy_score": 85,
          "compatibility_score": 90,
          "safety_score": 80,
          "cost_score": 70,
          "overall_score": 82,
          "side_effects": ["effect1", "effect2"],
          "contraindications": ["contraindication1"],
          "supporting_evidence": "Evidence details"
        }
      ]
    }
    
    Ensure all recommendations are evidence-based and backed by scientific research.
    """

def _get_homeopathy_system_prompt() -> str:
    """Get system prompt for homeopathy agent"""
    return """
    You are a specialized medical AI trained to provide homeopathic therapy recommendations.
    
    Use knowledge from homeopathic repertories, traditional wisdom, and holistic health practices.
    
    For each therapy recommendation, provide:
    1. Remedy name
    2. Description
    3. Efficacy score based on symptom similarity (0-100)
    4. Compatibility score based on constitutional type (0-100)
    5. Safety score (0-100)
    6. Cost score (higher = more affordable, 0-100)
    7. Potency and frequency
    8. Lifestyle modifications
    9. Supporting evidence (traditional sources, case studies)
    
    Your response must be well-structured and in JSON format with a 'therapies' array.
    
    Response format example:
    {
      "therapies": [
        {
          "therapy_type": "homeopathy",
          "therapy_name": "Remedy Name",
          "description": "Detailed description",
          "efficacy_score": 85,
          "compatibility_score": 90,
          "safety_score": 95,
          "cost_score": 80,
          "overall_score": 88,
          "side_effects": ["effect1", "effect2"],
          "contraindications": ["contraindication1"],
          "supporting_evidence": "Traditional evidence details"
        }
      ]
    }
    
    Focus on the principle of 'like cures like' and individualize treatments.
    """

def _get_combined_system_prompt() -> str:
    """Get system prompt for combined agents"""
    return """
    You are a specialized medical AI trained to provide both allopathic and homeopathic therapy recommendations.
    
    For allopathic recommendations, use evidence-based medical knowledge from PubMed, Clinical Trials, FDA, and WHO data.
    
    For homeopathic recommendations, use knowledge from homeopathic repertories, traditional wisdom, and holistic health practices.
    
    For each therapy recommendation, provide:
    1. Therapy type (allopathy or homeopathy)
    2. Therapy/Remedy name
    3. Description
    4. Efficacy score (0-100)
    5. Compatibility score based on patient profile (0-100)
    6. Safety score (0-100)
    7. Cost score (higher = more affordable, 0-100)
    8. Side effects
    9. Contraindications
    10. Supporting evidence (citations or research basis for allopathy, traditional sources for homeopathy)
    
    Your response must be well-structured and in JSON format with a 'therapies' array.
    
    Response format example:
    {
      "therapies": [
        {
          "therapy_type": "allopathy",
          "therapy_name": "Allopathic Treatment",
          "description": "Detailed description",
          "efficacy_score": 85,
          "compatibility_score": 90,
          "safety_score": 80,
          "cost_score": 70,
          "overall_score": 82,
          "side_effects": ["effect1", "effect2"],
          "contraindications": ["contraindication1"],
          "supporting_evidence": "Evidence details"
        },
        {
          "therapy_type": "homeopathy",
          "therapy_name": "Homeopathic Remedy",
          "description": "Detailed description",
          "efficacy_score": 75,
          "compatibility_score": 85,
          "safety_score": 95,
          "cost_score": 90,
          "overall_score": 85,
          "side_effects": ["effect1", "effect2"],
          "contraindications": ["contraindication1"],
          "supporting_evidence": "Traditional evidence details"
        }
      ]
    }
    
    Provide a balanced view of both approaches, highlighting strengths of each.
    """

def _get_mock_recommendations(agent_type: str) -> List[Dict[str, Any]]:
    """Mock therapy recommendations when OpenAI API key is not available (for development only)"""
    logger.warning("Using mock therapy recommendations - for development only")
    
    recommendations = []
    
    if agent_type in ["allopathy", "both"]:
        recommendations.append({
            "therapy_type": "allopathy",
            "therapy_name": "Standard Treatment Protocol",
            "description": "This is a mock allopathic therapy recommendation. In a real implementation, this would be generated by the OpenAI API.",
            "efficacy_score": 80,
            "compatibility_score": 85,
            "safety_score": 75,
            "cost_score": 60,
            "overall_score": 75,
            "side_effects": ["Common side effect 1", "Common side effect 2"],
            "contraindications": ["Known contraindication"],
            "supporting_evidence": "This would reference medical literature and studies."
        })
    
    if agent_type in ["homeopathy", "both"]:
        recommendations.append({
            "therapy_type": "homeopathy",
            "therapy_name": "Homeopathic Remedy",
            "description": "This is a mock homeopathic therapy recommendation. In a real implementation, this would be generated by the OpenAI API.",
            "efficacy_score": 70,
            "compatibility_score": 90,
            "safety_score": 95,
            "cost_score": 80,
            "overall_score": 85,
            "side_effects": ["Rare side effect"],
            "contraindications": ["Specific contraindication"],
            "supporting_evidence": "This would reference traditional homeopathic sources."
        })
    
    return recommendations
