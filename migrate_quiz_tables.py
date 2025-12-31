"""
Migration script to add quiz tables to existing database
Run this with: python migrate_quiz_tables.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, QuizQuestion, QuizAttempt, QuizAnswer

def migrate_quiz_tables():
    """Add quiz tables to existing database"""
    print("🔄 Starting quiz tables migration...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create quiz tables
            print("📦 Creating quiz_questions table...")
            QuizQuestion.__table__.create(db.engine, checkfirst=True)
            
            print("📦 Creating quiz_attempts table...")
            QuizAttempt.__table__.create(db.engine, checkfirst=True)
            
            print("📦 Creating quiz_answers table...")
            QuizAnswer.__table__.create(db.engine, checkfirst=True)
            
            print("✅ Quiz tables migration completed successfully!")
            print("\nNew tables created:")
            print("  - quiz_questions")
            print("  - quiz_attempts")
            print("  - quiz_answers")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

if __name__ == '__main__':
    success = migrate_quiz_tables()
    sys.exit(0 if success else 1)
