from flask import Flask
from flask_cors import CORS
from app.config import config
from app.models import db

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
    
    # Enable CORS untuk semua routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Create tables if not exist
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Register blueprints
    from app.routes import api_bp
    from app.auth_routes import auth_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)  # Auth already has /api/auth prefix
    
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
