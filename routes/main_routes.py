import logging
import os
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from extensions import db  # Import db from extensions, not models
from models import User, Profile, Report, Therapy  # Import only the models from models
from utils.ner_extraction import extract_entities_from_text
from utils.gemini_integration import get_therapy_recommendations, select_medical_approach
from utils.therapy_ranking import rank_therapies
from utils.pdf_processor import extract_text_from_pdf, save_uploaded_pdf
from flask_login import login_required, current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile creation and updates"""
    if request.method == 'POST':
        # For demo purposes, we're using session instead of user authentication
        session['profile'] = {
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'weight': request.form.get('weight'),
            'height': request.form.get('height'),
            'lifestyle': request.form.get('lifestyle'),
            'medical_history': request.form.get('medical_history'),
            'allergies': request.form.get('allergies'),
            'current_medications': request.form.get('current_medications')
        }
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.analysis'))
    
    return render_template('profile.html', profile=session.get('profile', {}))

@main_bp.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    """Handle pathology report upload and analysis"""
    if request.method == 'POST':
        report_text = request.form.get('report_text')
        report_file = request.files.get('report_file')
        
        # Check if we have a file upload
        if report_file and report_file.filename and report_file.filename.endswith('.pdf'):
            try:
                logger.info(f"Processing uploaded PDF file: {report_file.filename}")
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(report_file)
                
                # Save PDF file for reference
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                safe_filename = secure_filename(report_file.filename)
                save_path = save_uploaded_pdf(report_file, uploads_dir)
                
                if not pdf_text or not pdf_text.strip():
                    flash('The uploaded PDF did not contain any extractable text. Please try a different file or enter text manually.', 'warning')
                    return redirect(url_for('main.analysis'))
                
                # Use the PDF text for analysis
                report_text = pdf_text
                
                # Store original filename in session
                session['pdf_filename'] = safe_filename
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}")
                flash(f'Error processing PDF: {str(e)}', 'error')
                return redirect(url_for('main.analysis'))
        
        # Check if we have any text to process
        if not report_text or not report_text.strip():
            flash('Please either upload a PDF or enter report text', 'error')
            return redirect(url_for('main.analysis'))
        
        try:
            # Extract entities from the report text
            extracted_entities = extract_entities_from_text(report_text)
            
            # Store in session for this demo
            session['report'] = {
                'text': report_text,
                'extracted_entities': extracted_entities
            }
            
            # Redirect to agent selection
            return redirect(url_for('main.select_agent'))
        except Exception as e:
            logger.error(f"Error processing report: {str(e)}")
            flash(f'Error processing report: {str(e)}', 'error')
    
    return render_template('analysis.html')

@main_bp.route('/select-agent', methods=['GET', 'POST'])
def select_agent():
    """Select treatment agent (allopathy, homeopathy, or both)"""
    if request.method == 'POST':
        agent_type = request.form.get('agent_type')
        query = request.form.get('query', 'What are my therapy options?')
        
        if not agent_type:
            flash('Please select an agent type', 'error')
            return redirect(url_for('main.select_agent'))
        
        try:
            # Get profile and report data from session
            profile = session.get('profile', {})
            report = session.get('report', {})
            
            # Get therapy recommendations
            therapy_recommendations = get_therapy_recommendations(
                agent_type,
                profile,
                report.get('extracted_entities', {}),
                query
            )
            
            # Rank therapies
            ranked_therapies = rank_therapies(therapy_recommendations)
            
            # Store in session
            session['therapies'] = ranked_therapies
            session['agent_type'] = agent_type
            
            return redirect(url_for('main.results'))
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            flash(f'Error getting recommendations: {str(e)}', 'error')
    
    return render_template(
        'select_agent.html',
        report_entities=session.get('report', {}).get('extracted_entities', {})
    )

@main_bp.route('/approach-selector', methods=['GET', 'POST'])
def approach_selector():
    """Select the best medical approach based on user's health query"""
    if request.method == 'POST':
        health_query = request.form.get('health_query')
        if not health_query:
            flash('Please enter your health concern', 'error')
            return redirect(url_for('main.approach_selector'))
        
        try:
            # Use Gemini AI to analyze the query and determine the best approach
            logger.debug(f"Processing health query with Gemini AI: {health_query}")
            approach, reason = select_medical_approach(health_query)
            
            return render_template(
                'approach_result.html',
                query=health_query,
                approach=approach,
                reason=reason
            )
        except Exception as e:
            logger.error(f"Error selecting medical approach: {str(e)}")
            flash(f"Error processing your query: {str(e)}", "error")
            return redirect(url_for('main.approach_selector'))
    
    return render_template('approach_selector.html')

@main_bp.route('/api/select-approach', methods=['POST'])
def api_select_approach():
    """API endpoint for selecting the best approach"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing health query'}), 400
    
    try:
        approach, reason = select_medical_approach(data['query'])
        return jsonify({
            'approach': approach,
            'reason': reason
        })
    except Exception as e:
        logger.error(f"API error selecting medical approach: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/results')
def results():
    """Display therapy results and recommendations"""
    agent_type = session.get('agent_type', 'both')
    therapies = session.get('therapies', [])
    profile = session.get('profile', {})
    report_entities = session.get('report', {}).get('extracted_entities', {})
    
    # Debug the therapies data
    logger.debug(f"Therapies data for results page: {therapies}")
    
    # Ensure therapies is a list
    if not isinstance(therapies, list):
        logger.warning(f"Therapies is not a list: {type(therapies)}. Converting to empty list.")
        therapies = []
    
    # Ensure each therapy has the required fields
    for therapy in therapies:
        if not isinstance(therapy, dict):
            logger.warning(f"Therapy is not a dict: {type(therapy)}. Skipping.")
            continue
            
        # Ensure required fields exist with default values
        therapy.setdefault('therapy_type', 'unknown')
        therapy.setdefault('therapy_name', 'Unknown Therapy')
        therapy.setdefault('description', 'No description available')
        therapy.setdefault('efficacy_score', 0)
        therapy.setdefault('compatibility_score', 0)
        therapy.setdefault('safety_score', 0)
        therapy.setdefault('cost_score', 0)
        therapy.setdefault('overall_score', 0)
        therapy.setdefault('side_effects', [])
        therapy.setdefault('contraindications', [])
        therapy.setdefault('supporting_evidence', '')
    
    return render_template(
        'results.html',
        agent_type=agent_type,
        therapies=therapies,
        profile=profile,
        entities=report_entities
    )

@main_bp.route('/reports')
@login_required
def reports():
    """Display user's reports history"""
    # Get reports for the current user
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    
    return render_template(
        'reports.html',
        reports=user_reports
    )




