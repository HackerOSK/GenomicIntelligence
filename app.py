import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, login_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "dev_key_for_testing")
    
    # Use ProxyFix for proper URL generation with HTTPS
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///precision_medicine.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        # Import models - import the module, not individual classes
        import models
        
        # Create all tables
        db.create_all()
        
        # Import routes
        from routes.main_routes import main_bp
        from routes.api_routes import api_bp
        from routes.auth_routes import auth_bp
        
        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(auth_bp)
        
        logger.info("Application initialized successfully")
    
    return app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

