import logging
import json
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def extract_entities_from_text(text: str) -> Dict[str, Any]:
    """
    Extract medical entities from text using spaCy
    
    In a production implementation, this would use a proper medical NER model like BioBERT
    For this demo, we'll use a simplified implementation with some heuristics
    
    Args:
        text: The text to extract entities from
        
    Returns:
        Dictionary of extracted entities
    """
    logger.debug(f"Extracting entities from text: {text[:100]}...")
    
    # Initialize results
    entities = {
        "diseases": [],
        "symptoms": [],
        "lab_values": [],
        "genes": [],
        "medications": []
    }
    
    # Simple disease keywords
    disease_keywords = [
        "diabetes", "hypertension", "cancer", "asthma", "arthritis", 
        "alzheimer", "parkinson", "hypothyroidism", "hyperthyroidism", 
        "fibroids", "covid", "tuberculosis", "pneumonia", "anemia"
    ]
    
    # Simple symptom keywords
    symptom_keywords = [
        "pain", "fever", "cough", "fatigue", "headache", 
        "nausea", "vomiting", "dizziness", "rash", "swelling",
        "shortness of breath", "insomnia", "anxiety", "depression"
    ]
    
    # Simple lab test keywords (with units)
    lab_value_patterns = [
        (r"hemoglobin", "g/dL"),
        (r"glucose", "mg/dL"),
        (r"cholesterol", "mg/dL"),
        (r"triglycerides", "mg/dL"),
        (r"creatinine", "mg/dL"),
        (r"TSH", "mIU/L"),
        (r"T3", "ng/dL"),
        (r"T4", "μg/dL"),
        (r"WBC", "cells/μL"),
        (r"RBC", "million/μL")
    ]
    
    # Simple gene mutation patterns
    gene_patterns = [
        "BRCA1", "BRCA2", "EGFR", "KRAS", "HER2", "TP53", 
        "BRAF", "MLH1", "MSH2", "APC", "RET", "PTEN"
    ]
    
    # Medication patterns
    medication_patterns = [
        "aspirin", "acetaminophen", "ibuprofen", "lisinopril", 
        "metformin", "atorvastatin", "levothyroxine", "amlodipine", 
        "albuterol", "metoprolol", "simvastatin", "omeprazole"
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Extract diseases
    for disease in disease_keywords:
        if disease.lower() in text_lower:
            entities["diseases"].append(disease)
    
    # Extract symptoms
    for symptom in symptom_keywords:
        if symptom.lower() in text_lower:
            entities["symptoms"].append(symptom)
    
    # Extract lab values (simple implementation)
    for lab_name, unit in lab_value_patterns:
        if lab_name.lower() in text_lower:
            # Add as a placeholder - in a real implementation we would extract the actual value
            entities["lab_values"].append({
                "name": lab_name,
                "value": "Detected",
                "unit": unit
            })
    
    # Extract genes (case-sensitive)
    for gene in gene_patterns:
        if gene in text:
            entities["genes"].append(gene)
    
    # Extract medications
    for med in medication_patterns:
        if med.lower() in text_lower:
            entities["medications"].append(med)
    
    logger.debug(f"Extracted entities: {json.dumps(entities)}")
    return entities
