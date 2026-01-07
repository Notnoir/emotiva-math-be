from flask import Flask
from flask_cors import CORS
from app.config import config
from app.models import db
import sys

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_app(config_name='default'):
    """
    Application Factory Pattern
    Membuat dan mengkonfigurasi Flask application
    """
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Create tables if not exist
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully")
    
    # Register blueprints
    from app.routes import api_bp
    from app.auth_routes import auth_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)  # Auth already has /api/auth prefix
    
    # Enable CORS setelah blueprint registered - PENTING!
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False,
            "send_wildcard": False,
            "always_send": True,
            "max_age": 3600
        }
    })
    
    # Health check route (tanpa prefix)
    @app.route('/')
    def index():
        return {
            'status': 'success',
            'message': 'EMOTIVA-MATH Backend API is running',
            'version': '1.0.0',
            'math_topic': app.config['MATH_TOPIC'],
            'database': 'SQLite - Connected'
        }
    
    return app
