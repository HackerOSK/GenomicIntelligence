import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from extensions import db  # Import db from extensions, not models
from models import User  # Import only the models from models
from forms import LoginForm, RegistrationForm

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
            
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug("Register route accessed")
    if current_user.is_authenticated:
        logger.debug("User already authenticated, redirecting to index")
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if request.method == 'POST':
        logger.debug(f"Form data received: {request.form}")
        
    if form.validate_on_submit():
        logger.debug("Form validated successfully")
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            logger.debug(f"User created: {user.username}, {user.email}")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
    elif request.method == 'POST':
        logger.debug(f"Form validation errors: {form.errors}")
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))




