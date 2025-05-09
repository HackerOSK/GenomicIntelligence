# AI Agent Workflow in Precision Medicine Platform

## Overview

This document explains the AI agent architecture used in our Precision Medicine Platform. The system employs a multi-agent approach to provide personalized medical recommendations across different treatment philosophies (Allopathy, Homeopathy, and Ayurveda).

## Agent Architecture

### Base Agent Design

The system uses a class-based architecture with a base `TreatmentAgent` class that defines the common interface and functionality for all specialized agents. This base class handles:

- API communication with LLM providers
- Data formatting and processing
- Response parsing and validation
- Error handling and logging

### Specialized Agents

Three specialized agents extend the base agent, each with unique knowledge and recommendation approaches:

1. **AllopathyAgent**: 
   - Focuses on conventional medicine using evidence-based approaches
   - Sources knowledge from PubMed, Clinical Trials, FDA, and WHO data
   - Emphasizes efficacy based on scientific research

2. **HomeopathyAgent**: 
   - Specializes in homeopathic remedies and holistic approaches
   - Uses knowledge from homeopathic repertories and traditional wisdom
   - Focuses on the principle of "like cures like" and individualized treatments

3. **AyurvedaAgent**: 
   - Provides recommendations based on traditional Ayurvedic principles
   - Incorporates dosha balancing and natural healing processes
   - Includes lifestyle and dietary recommendations

## LLM Integration

The system integrates with multiple Large Language Model providers for flexibility:

- **Anthropic Claude**: Primary model for nuanced medical reasoning
- **OpenAI GPT-4o**: Alternative model with strong medical knowledge
- **Google Gemini**: Tertiary option for additional perspective

The system automatically selects the appropriate LLM based on available API keys and falls back gracefully if a service is unavailable.

## Workflow Process

### 1. Approach Selection

When a user submits a health query, the system can:
- Allow the user to explicitly choose their preferred treatment philosophy
- Automatically recommend the most appropriate approach using the `select_approach_with_agent()` function
- Provide recommendations from all approaches for comparison

The automatic selection analyzes the nature of the health concern and recommends:
- **Allopathy**: For acute or urgent conditions
- **Homeopathy**: For chronic or long-lasting diseases
- **Ayurveda**: For general wellness, lifestyle issues, and preventive care

### 2. Data Collection and Processing

The system collects and processes:
- User profile information (age, gender, medical history)
- Extracted entities from pathology reports
- Specific health queries or concerns

This data is formatted into a structured JSON object that serves as context for the AI agents.

### 3. Agent Recommendation Generation

The `get_agent_recommendations()` function:
- Selects the appropriate specialized agent(s) based on the chosen approach
- Prepares a system prompt that guides the LLM's response
- Sends the user data and prompt to the LLM
- Processes the response into a structured format

### 4. Response Structure

All agents return recommendations in a consistent JSON format with:
- Therapy name and type
- Detailed description
- Efficacy score (0-100)
- Compatibility score based on patient profile (0-100)
- Safety score (0-100)
- Cost score (higher = more affordable, 0-100)
- Overall score (weighted average)
- Side effects and contraindications
- Supporting evidence or research basis

### 5. Visualization and Presentation

The recommendations are presented to the user through:
- Therapy cards with expandable details
- Comparative charts showing scores across different metrics
- Side-by-side comparison of different treatment approaches

## Key Benefits

1. **Personalization**: Recommendations are tailored to the user's specific health profile and concerns
2. **Multiple Perspectives**: Users can explore different treatment philosophies for a comprehensive view
3. **Evidence-Based**: All recommendations include supporting evidence and efficacy scores
4. **Transparency**: Clear explanation of how recommendations are generated and scored
5. **Flexibility**: The system can adapt to different user preferences and health needs

## Technical Implementation

The agent system is implemented using:
- Python for backend logic
- Flask for web framework
- LangChain/direct API integration for LLM communication
- JSON for structured data exchange
- Chart.js for visualization of comparative metrics

## Future Enhancements

Planned enhancements to the agent system include:
- Fine-tuning specialized models for each treatment philosophy
- Incorporating real-time medical database lookups
- Adding more treatment philosophies (Traditional Chinese Medicine, etc.)
- Implementing agent memory for continuity across sessions
- Developing a feedback loop to improve recommendations over time

---

This multi-agent architecture allows our system to provide comprehensive, personalized medical recommendations while respecting different treatment philosophies and maintaining a consistent user experience.