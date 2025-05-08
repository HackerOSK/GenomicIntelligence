import logging
import os
from flask import Blueprint, request, jsonify, send_file, session, current_app
from utils.ner_extraction import extract_entities_from_text
from utils.gemini_integration import get_therapy_recommendations, select_medical_approach
from utils.therapy_ranking import rank_therapies
from utils.agent_integration import get_agent_recommendations, select_approach_with_agent
from utils.pdf_generator import generate_therapy_report

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/extract-entities', methods=['POST'])
def extract_entities():
    """API endpoint to extract entities from text"""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        entities = extract_entities_from_text(data['text'])
        return jsonify({'entities': entities})
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get therapy recommendations"""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['agent_type', 'profile', 'entities', 'query']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    try:
        recommendations = get_therapy_recommendations(
            data['agent_type'],
            data['profile'],
            data['entities'],
            data['query']
        )
        
        ranked_therapies = rank_therapies(recommendations)
        
        return jsonify({'therapies': ranked_therapies})
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/agent-recommendations', methods=['POST'])
def agent_recommendations():
    """API endpoint to get therapy recommendations using SmolAgents"""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['agent_type', 'profile', 'entities', 'query']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    try:
        # Use SmolAgents for recommendations
        recommendations = get_agent_recommendations(
            data['agent_type'],
            data['profile'],
            data['entities'],
            data['query']
        )
        
        ranked_therapies = rank_therapies(recommendations)
        
        return jsonify({'therapies': ranked_therapies})
    except Exception as e:
        logger.error(f"Error getting agent recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/select-approach-agent', methods=['POST'])
def select_approach_agent():
    """API endpoint to select medical approach using SmolAgents"""
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing health query'}), 400
    
    try:
        approach, reason = select_approach_with_agent(data['query'])
        return jsonify({
            'approach': approach,
            'reason': reason
        })
    except Exception as e:
        logger.error(f"Error selecting approach with agent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/export-report', methods=['GET'])
def export_report():
    """API endpoint to export therapy report as PDF"""
    try:
        # Get data from session
        agent_type = session.get('agent_type', 'both')
        therapies = session.get('therapies', [])
        profile = session.get('profile', {})
        report = session.get('report', {})
        extracted_entities = report.get('extracted_entities', {})
        query = request.args.get('query', 'What are my therapy options?')
        
        if not therapies:
            return jsonify({'error': 'No therapy recommendations found in session'}), 400
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate the PDF report
        pdf_path = generate_therapy_report(
            profile=profile,
            entities=extracted_entities,
            therapies=therapies,
            agent_type=agent_type,
            query=query,
            output_path=output_dir
        )
        
        # Return the file
        filename = os.path.basename(pdf_path)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return jsonify({'error': str(e)}), 500
