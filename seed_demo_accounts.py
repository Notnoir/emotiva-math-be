"""
Seed demo accounts for testing authentication
Creates teacher and student accounts with demo credentials
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User
from app.auth_utils import hash_password

def seed_demo_accounts():
    """
    Create demo accounts:
    1. Teacher: teacher@demo.com / password123
    2. Student: student@demo.com / password123
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("🌱 Seeding demo accounts...\n")
            
            # Check if demo accounts already exist
            existing_teacher = User.query.filter_by(email='teacher@demo.com').first()
            existing_student = User.query.filter_by(email='student@demo.com').first()
            
            if existing_teacher:
                print("⏭️  Teacher demo account already exists")
            else:
                # Create teacher account
                teacher = User(
                    nama='Guru Demo',
                    email='teacher@demo.com',
                    password_hash=hash_password('password123'),
                    role='teacher'
                )
                db.session.add(teacher)
                print("✅ Created teacher account:")
                print("   Email: teacher@demo.com")
                print("   Password: password123")
            
            if existing_student:
                print("⏭️  Student demo account already exists")
            else:
                # Create student account
                student = User(
                    nama='Siswa Demo',
                    email='student@demo.com',
                    password_hash=hash_password('password123'),
                    role='student',
                    gaya_belajar='visual',
                    level='pemula'
                )
                db.session.add(student)
                print("✅ Created student account:")
                print("   Email: student@demo.com")
                print("   Password: password123")
            
            db.session.commit()
            
            print("\n✨ Demo accounts seeded successfully!")
            print("\n📝 You can now login with:")
            print("   👨‍🏫 Teacher: teacher@demo.com / password123")
            print("   👨‍🎓 Student: student@demo.com / password123")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Seeding failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🔐 EMOTIVA-MATH - Demo Accounts Seeder\n")
    success = seed_demo_accounts()
    
    if success:
        print("\n✅ Seeding complete!")
        sys.exit(0)
    else:
        print("\n❌ Seeding failed!")
        sys.exit(1)
