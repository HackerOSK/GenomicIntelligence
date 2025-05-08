"""
Agent Integration Module

This module integrates with various AI models to provide specialized medical recommendations
across different treatment philosophies.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# API keys for different LLM providers
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

class TreatmentAgent:
    """Base class for treatment philosophy agents"""
    
    def __init__(self, agent_type: str):
        """
        Initialize a treatment agent
        
        Args:
            agent_type: The type of agent (allopathy, homeopathy, ayurveda)
        """
        self.agent_type = agent_type
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent type (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement _get_system_prompt()")
    
    def get_therapy_recommendations(self, profile: Dict[str, Any], 
                                   entities: Dict[str, Any], 
                                   query: str) -> List[Dict[str, Any]]:
        """
        Get therapy recommendations based on user profile, extracted entities, and query
        
        Args:
            profile: User profile data
            entities: Extracted entities from pathology report
            query: User query
            
        Returns:
            List of therapy recommendations
        """
        # Prepare user data for the prompt
        user_data = {"profile": profile, "entities": entities, "query": query}
        user_data_json = json.dumps(user_data, indent=2)
        
        # Get system prompt
        system_prompt = self._get_system_prompt()
        
        # Create full prompt
        full_prompt = f"{system_prompt}\n\nUser Data:\n{user_data_json}\n\nProvide therapy recommendations in JSON format."
        
        # Get response from appropriate model
        if ANTHROPIC_API_KEY:
            response_text = self._call_anthropic_api(system_prompt, user_data_json)
        elif OPENAI_API_KEY:
            response_text = self._call_openai_api(system_prompt, user_data_json)
        elif GEMINI_API_KEY:
            response_text = self._call_gemini_api(full_prompt)
        else:
            logger.error(f"No API keys available for {self.agent_type} agent")
            return []
        
        # Parse the response text to extract JSON
        try:
            # First, try to parse the entire response as JSON
            recommendations = json.loads(response_text)
            
            # Ensure we have the therapies field
            if "therapies" not in recommendations:
                logger.error(f"Invalid response format from {self.agent_type} agent: missing 'therapies' field")
                # Try to extract just the therapies array if possible
                if isinstance(recommendations, list) and len(recommendations) > 0:
                    return recommendations
                return []
            
            return recommendations["therapies"]
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract JSON using pattern matching
            logger.warning(f"Response from {self.agent_type} agent is not valid JSON, attempting to extract JSON portion")
            
            # Look for JSON-like patterns
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            
            if json_match:
                try:
                    extracted_json = json.loads(json_match.group(1))
                    if "therapies" in extracted_json:
                        return extracted_json["therapies"]
                    return []
                except:
                    logger.error(f"Failed to extract valid JSON from {self.agent_type} agent response")
                    return []
            else:
                logger.error(f"No JSON-like pattern found in {self.agent_type} agent response")
                return []
    
    def _call_anthropic_api(self, system_prompt: str, user_data_json: str) -> str:
        """Call Anthropic API to get therapy recommendations"""
        try:
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 2000,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the user data:\n{user_data_json}\n\nPlease provide therapy recommendations."}
                ],
                "temperature": 0.2
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            return response.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            return ""
    
    def _call_openai_api(self, system_prompt: str, user_data_json: str) -> str:
        """Call OpenAI API to get therapy recommendations"""
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the user data:\n{user_data_json}\n\nPlease provide therapy recommendations."}
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return ""
    
    def _call_gemini_api(self, full_prompt: str) -> str:
        """Call Gemini API to get therapy recommendations"""
        try:
            import google.generativeai as genai
            
            # Configure the Gemini API
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Use Gemini API to generate content with the Gemini Pro model
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            response = model.generate_content(full_prompt)
            
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return ""


class AllopathyAgent(TreatmentAgent):
    """Agent specialized in allopathic (conventional) medicine"""
    
    def __init__(self):
        super().__init__("allopathy")
    
    def _get_system_prompt(self) -> str:
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


class HomeopathyAgent(TreatmentAgent):
    """Agent specialized in homeopathic medicine"""
    
    def __init__(self):
        super().__init__("homeopathy")
    
    def _get_system_prompt(self) -> str:
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


class AyurvedaAgent(TreatmentAgent):
    """Agent specialized in Ayurvedic medicine"""
    
    def __init__(self):
        super().__init__("ayurveda")
    
    def _get_system_prompt(self) -> str:
        return """
        You are a specialized medical AI trained to provide Ayurvedic therapy recommendations.
        
        Use knowledge from traditional Ayurvedic texts, dosha principles, and holistic wellness approaches.
        
        For each therapy recommendation, provide:
        1. Remedy name
        2. Description
        3. Efficacy score based on traditional usage (0-100)
        4. Compatibility score based on dosha type (0-100)
        5. Safety score (0-100)
        6. Cost score (higher = more affordable, 0-100)
        7. Herbs and ingredients
        8. Lifestyle and dietary recommendations
        9. Supporting evidence (traditional texts, historical usage)
        
        Your response must be well-structured and in JSON format with a 'therapies' array.
        
        Response format example:
        {
          "therapies": [
            {
              "therapy_type": "ayurveda",
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
        
        Focus on balancing doshas and promoting natural healing processes.
        """


def get_agent_recommendations(agent_type: str, profile: Dict[str, Any],
                             entities: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """
    Get recommendations from the appropriate treatment agent
    
    Args:
        agent_type: The type of agent (allopathy, homeopathy, ayurveda, or all)
        profile: User profile data
        entities: Extracted entities from pathology report
        query: User query
        
    Returns:
        List of therapy recommendations
    """
    logger.debug(f"Getting recommendations from agent type: {agent_type}")
    
    # Check if we have any API keys available
    if not (OPENAI_API_KEY or ANTHROPIC_API_KEY or GEMINI_API_KEY):
        logger.error("No API keys available for any LLM provider")
        return []
    
    recommendations = []
    
    # Get recommendations from appropriate agent(s)
    if agent_type in ["allopathy", "all"]:
        try:
            allopathy_agent = AllopathyAgent()
            allopathy_recs = allopathy_agent.get_therapy_recommendations(profile, entities, query)
            recommendations.extend(allopathy_recs)
        except Exception as e:
            logger.error(f"Error getting allopathy recommendations: {str(e)}")
    
    if agent_type in ["homeopathy", "all"]:
        try:
            homeopathy_agent = HomeopathyAgent()
            homeopathy_recs = homeopathy_agent.get_therapy_recommendations(profile, entities, query)
            recommendations.extend(homeopathy_recs)
        except Exception as e:
            logger.error(f"Error getting homeopathy recommendations: {str(e)}")
    
    if agent_type in ["ayurveda", "all"]:
        try:
            ayurveda_agent = AyurvedaAgent()
            ayurveda_recs = ayurveda_agent.get_therapy_recommendations(profile, entities, query)
            recommendations.extend(ayurveda_recs)
        except Exception as e:
            logger.error(f"Error getting ayurveda recommendations: {str(e)}")
    
    return recommendations


def select_approach_with_agent(health_query: str) -> tuple:
    """
    Use an agent to determine the best medical approach based on a health query
    
    Args:
        health_query: User's health concern query
    
    Returns:
        tuple: (approach_name, reason)
    """
    logger.debug(f"Using agent to select medical approach for query: {health_query}")
    
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
    
    user_content = f"Health Query: {health_query}\n\nWhat is the most appropriate medical approach for this concern?"
    
    # Get response from appropriate model
    if ANTHROPIC_API_KEY:
        try:
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 300,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            response_text = response.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            response_text = ""
    elif OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1,
                "max_tokens": 300,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            response_text = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            response_text = ""
    elif GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            
            # Configure the Gemini API
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Use Gemini API to generate content with the Gemini Pro model
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            full_prompt = f"{system_prompt}\n\n{user_content}"
            response = model.generate_content(full_prompt)
            
            response_text = response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            response_text = ""
    else:
        logger.error("No API keys available for any LLM provider")
        return "Allopathy", "Default recommendation due to missing API keys."
    
    # Parse the response
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
                logger.error(f"Invalid approach value from agent: {approach}")
        else:
            logger.error("Missing required fields in agent response")
            
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
    
    # Fallback to rule-based selection
    import re
    query = health_query.lower()
    
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