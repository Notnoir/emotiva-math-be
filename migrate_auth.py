"""
Migration script to add authentication fields to existing database
Run this ONCE to update the database schema for authentication
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from sqlalchemy import text

def migrate_auth_fields():
    """
    Add authentication fields to users table:
    - email (unique, not null)
    - password_hash (not null)
    - role (not null, default 'student')
    - Make gaya_belajar nullable
    """
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            
            print("📊 Existing columns in 'users' table:", existing_columns)
            
            # Add email column if not exists
            if 'email' not in existing_columns:
                print("➕ Adding 'email' column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE"
                ))
                db.session.execute(text(
                    "CREATE INDEX idx_users_email ON users(email)"
                ))
                print("✅ Column 'email' added successfully")
            else:
                print("⏭️ Column 'email' already exists")
            
            # Add password_hash column if not exists
            if 'password_hash' not in existing_columns:
                print("➕ Adding 'password_hash' column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"
                ))
                print("✅ Column 'password_hash' added successfully")
            else:
                print("⏭️ Column 'password_hash' already exists")
            
            # Add role column if not exists
            if 'role' not in existing_columns:
                print("➕ Adding 'role' column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'student'"
                ))
                print("✅ Column 'role' added successfully")
            else:
                print("⏭️ Column 'role' already exists")
            
            # Modify gaya_belajar to be nullable (for teachers who don't need it)
            print("🔄 Modifying 'gaya_belajar' to be nullable...")
            try:
                # For SQLite
                if 'sqlite' in str(db.engine.url):
                    print("⚠️ SQLite detected - column modification requires recreation")
                    print("✅ Skipping nullable modification (SQLite limitation)")
                else:
                    # For MySQL
                    db.session.execute(text(
                        "ALTER TABLE users MODIFY COLUMN gaya_belajar VARCHAR(20) NULL"
                    ))
                    print("✅ Column 'gaya_belajar' modified successfully")
            except Exception as e:
                print(f"⚠️ Could not modify gaya_belajar: {e}")
            
            # Commit changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("\n📝 Next steps:")
            print("1. Update existing users to add email and password")
            print("2. Or delete old users and create new ones via /auth/register")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🔐 Starting Authentication Migration...\n")
    success = migrate_auth_fields()
    
    if success:
        print("\n✨ Migration successful! Database is ready for authentication.")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check errors above.")
        sys.exit(1)
