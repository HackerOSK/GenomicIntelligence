import os
import json
import logging
from typing import Dict, Any, List

import google.generativeai as genai

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_therapy_recommendations(agent_type: str, profile: Dict[str, Any],
                                entities: Dict[str, Any],
                                query: str) -> List[Dict[str, Any]]:
    """
    Get therapy recommendations from Gemini API based on agent type
    
    Args:
        agent_type: The type of agent (allopathy, homeopathy, or both)
        profile: User profile data
        entities: Extracted entities from pathology report
        query: User query
        
    Returns:
        List of therapy recommendations
    """
    logger.debug(
        f"Getting therapy recommendations from Gemini for agent type: {agent_type}"
    )

    # Handle empty API key
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not provided. Using mock data.")
        return _get_mock_recommendations(agent_type)

    # Create system prompt based on agent type
    if agent_type == "allopathy":
        system_prompt = _get_allopathy_system_prompt()
    elif agent_type == "homeopathy":
        system_prompt = _get_homeopathy_system_prompt()
    else:  # both
        system_prompt = _get_combined_system_prompt()

    # Prepare user data for the prompt
    user_data = {"profile": profile, "entities": entities, "query": query}

    # Serialize data for the prompt
    user_data_json = json.dumps(user_data, indent=2)

    try:
        # Use Gemini API to generate content with the Gemini Pro model
        model = genai.GenerativeModel('gemini-2.0-flash')

        full_prompt = f"{system_prompt}\n\nHere is the user data:\n{user_data_json}\n\nPlease provide therapy recommendations."

        response = model.generate_content(full_prompt)

        # Parse the response text to extract JSON
        response_text = response.text

        # Try to find and extract the JSON object from the response
        try:
            # First, try to parse the entire response as JSON
            recommendations = json.loads(response_text)

            # Ensure we have the therapies field
            if "therapies" not in recommendations:
                logger.error(
                    "Invalid response format from Gemini: missing 'therapies' field"
                )
                # Try to extract just the therapies array if possible
                if isinstance(recommendations,
                              list) and len(recommendations) > 0:
                    return recommendations
                return []

            return recommendations["therapies"]
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract JSON using pattern matching
            logger.warning(
                "Response is not valid JSON, attempting to extract JSON portion"
            )

            # Look for JSON-like patterns (this is a simplistic approach)
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)

            if json_match:
                try:
                    extracted_json = json.loads(json_match.group(1))
                    if "therapies" in extracted_json:
                        return extracted_json["therapies"]
                    return []
                except:
                    logger.error("Failed to extract valid JSON from response")
                    return []
            else:
                logger.error("No JSON-like pattern found in response")
                return []

    except Exception as e:
        logger.error(f"Error getting recommendations from Gemini: {str(e)}")
        logger.error(f"Full error details: {e}")
        return _get_mock_recommendations(agent_type)


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
          "compatibility_score": 95,
          "safety_score": 90,
          "cost_score": 85,
          "overall_score": 86,
          "side_effects": ["effect1", "effect2"],
          "contraindications": ["contraindication1"],
          "supporting_evidence": "Traditional evidence details"
        }
      ]
    }
    
    Provide a balanced view from both traditional medicine and complementary approaches.
    """


def _get_mock_recommendations(agent_type: str) -> List[Dict[str, Any]]:
    """Mock therapy recommendations when Gemini API key is not available (for development only)"""
    logger.warning("Using mock therapy recommendations - for development only")

    recommendations = []

    if agent_type in ["allopathy", "both"]:
        recommendations.append({
            "therapy_type":
            "allopathy",
            "therapy_name":
            "Standard Treatment Protocol",
            "description":
            "This is a mock allopathic therapy recommendation. In a real implementation, this would be generated by the Gemini API.",
            "efficacy_score":
            80,
            "compatibility_score":
            85,
            "safety_score":
            75,
            "cost_score":
            60,
            "overall_score":
            75,
            "side_effects": ["Common side effect 1", "Common side effect 2"],
            "contraindications": ["Known contraindication"],
            "supporting_evidence":
            "This would reference medical literature and studies."
        })

    if agent_type in ["homeopathy", "both"]:
        recommendations.append({
            "therapy_type":
            "homeopathy",
            "therapy_name":
            "Homeopathic Remedy",
            "description":
            "This is a mock homeopathic therapy recommendation. In a real implementation, this would be generated by the Gemini API.",
            "efficacy_score":
            70,
            "compatibility_score":
            90,
            "safety_score":
            95,
            "cost_score":
            80,
            "overall_score":
            85,
            "side_effects": ["Minimal side effect 1"],
            "contraindications": ["Rare contraindication"],
            "supporting_evidence":
            "This would reference traditional homeopathic texts and case studies."
        })

    return recommendations


def select_medical_approach(health_query: str) -> tuple:
    """
    Use Gemini API to determine the best medical approach based on a health query
    
    Args:
        health_query: User's health concern query
    
    Returns:
        tuple: (approach_name, reason)
    """
    logger.debug(f"Using Gemini to select medical approach for query: {health_query}")
    
    # Handle empty API key
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not provided. Using rule-based approach selection.")
        return _rule_based_approach_selection(health_query)
    
    system_prompt = """
    You are a medical expert specializing in different treatment approaches. Your role is to recommend the most 
    suitable medical approach (Allopathy, Homeopathy, or Ayurveda) based on a health query.
    
    Guidelines for approach selection:
    - Allopathy: Recommend for acute or urgent conditions (e.g., severe pain, fever, infection, injury, emergency situations)
    - Homeopathy: Recommend for chronic or long-lasting diseases (e.g., asthma, arthritis, recurring issues, conditions persisting for months/years)
    - Ayurveda: Recommend for general wellness, lifestyle issues, digestion, detox, and preventive care
    
    Analyze the health query and respond with ONLY the following JSON format:
    {
        "recommended_approach": "APPROACH_NAME",
        "reason": "ONE_LINE_EXPLANATION"
    }
    
    Where APPROACH_NAME must be exactly one of: "Allopathy", "Homeopathy", or "Ayurveda".
    The reason should be a brief, one-line explanation.
    """
    
    try:
        # Use Gemini API to generate content
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        full_prompt = f"{system_prompt}\n\nHealth Query: {health_query}\n\nRecommended Approach:"
        
        response = model.generate_content(full_prompt)
        response_text = response.text
        
        # Try to extract the JSON response
        try:
            # First try to parse the entire response as JSON
            result = json.loads(response_text)
            
            if "recommended_approach" in result and "reason" in result:
                approach = result["recommended_approach"]
                reason = result["reason"]
                
                # Validate the approach is one of the expected values
                if approach in ["Allopathy", "Homeopathy", "Ayurveda"]:
                    return approach, reason
                else:
                    logger.error(f"Invalid approach value from Gemini: {approach}")
            else:
                logger.error("Missing required fields in Gemini response")
                
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract it
            logger.warning("Response is not valid JSON, attempting to extract JSON portion")
            
            # Look for JSON-like patterns
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            
            if json_match:
                try:
                    extracted_json = json.loads(json_match.group(1))
                    if "recommended_approach" in extracted_json and "reason" in extracted_json:
                        approach = extracted_json["recommended_approach"]
                        reason = extracted_json["reason"]
                        
                        # Validate the approach
                        if approach in ["Allopathy", "Homeopathy", "Ayurveda"]:
                            return approach, reason
                except:
                    logger.error("Failed to extract valid JSON from response")
    
    except Exception as e:
        logger.error(f"Error getting approach selection from Gemini: {str(e)}")
    
    # Fallback to rule-based selection if Gemini fails
    return _rule_based_approach_selection(health_query)


def _rule_based_approach_selection(query: str) -> tuple:
    """
    Fallback rule-based approach selection if Gemini API fails
    
    Args:
        query: User's health query
        
    Returns:
        tuple: (approach_name, reason)
    """
    query = query.lower()
    
    # Allopathy indicators: acute/urgent conditions
    allopathy_patterns = [
        r'sudden', r'acute', r'severe', r'pain', r'fever', r'infection',
        r'headache', r'injury', r'wound', r'bleeding', r'broken', r'fracture',
        r'emergency', r'urgent', r'immediate', r'antibiotics', r'surgery',
        r'accident', r'heart attack', r'stroke', r'seizure'
    ]
    
    # Homeopathy indicators: chronic conditions
    homeopathy_patterns = [
        r'chronic', r'long[\s-]*term', r'recurring', r'years', r'months',
        r'persistent', r'asthma', r'arthritis', r'allergy', r'diabetes',
        r'thyroid', r'autoimmune', r'eczema', r'psoriasis', r'migraine',
        r'depression', r'anxiety', r'sleep', r'insomnia'
    ]
    
    # Ayurveda indicators: wellness/lifestyle/prevention
    ayurveda_patterns = [
        r'wellness', r'balance', r'diet', r'lifestyle', r'digestion',
        r'detox', r'cleanse', r'prevention', r'dosha', r'energy',
        r'fatigue', r'stress', r'meditation', r'yoga', r'weight',
        r'metabolism', r'immunity', r'rejuvenation', r'holistic'
    ]
    
    # Count matches for each approach
    import re
    allopathy_count = sum(1 for pattern in allopathy_patterns if re.search(pattern, query))
    homeopathy_count = sum(1 for pattern in homeopathy_patterns if re.search(pattern, query))
    ayurveda_count = sum(1 for pattern in ayurveda_patterns if re.search(pattern, query))
    
    # Determine the approach with the most matches
    if allopathy_count >= homeopathy_count and allopathy_count >= ayurveda_count:
        return "Allopathy", "Best for acute conditions requiring immediate relief."
    elif homeopathy_count >= allopathy_count and homeopathy_count >= ayurveda_count:
        return "Homeopathy", "Ideal for chronic or long-term health issues."
    else:
        return "Ayurveda", "Recommended for lifestyle balance and holistic wellness."
