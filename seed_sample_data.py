"""
Seed sample data untuk testing dashboard
Creates sample users, materials, quizzes, emotions, and learning logs
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User, TeacherMaterial, QuizAttempt, Emotion, LearningLog
from app.auth_utils import hash_password

def seed_sample_data():
    """Create sample data for dashboard"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🌱 Seeding sample data...\n")
            
            # 1. Create sample students
            print("👥 Creating sample students...")
            students = []
            gaya_belajar_options = ['visual', 'auditori', 'kinestetik']
            level_options = ['pemula', 'menengah', 'mahir']
            
            student_names = [
                'Andi Pratama', 'Budi Santoso', 'Citra Dewi', 'Dina Marlina',
                'Eko Prasetyo', 'Fitri Handayani', 'Gita Purnama', 'Hendra Wijaya',
                'Indah Sari', 'Joko Susanto'
            ]
            
            for i, name in enumerate(student_names):
                # Create email from name
                email = name.lower().replace(' ', '.') + '@student.com'
                
                existing = User.query.filter_by(email=email).first()
                if not existing:
                    student = User(
                        nama=name,
                        email=email,
                        password_hash=hash_password('student123'),  # Hash password
                        gaya_belajar=random.choice(gaya_belajar_options),
                        level=random.choice(level_options)
                    )
                    db.session.add(student)
                    students.append(student)
            
            db.session.commit()
            print(f"   ✅ Created {len(students)} students")
            
            # Refresh students list
            all_students = User.query.all()
            
            # 2. Create sample materials
            print("📚 Creating sample materials...")
            materials_data = [
                {
                    'judul': 'Pengenalan Kubus - Dasar',
                    'topik': 'kubus',
                    'level': 'pemula',
                    'konten': 'KUBUS adalah bangun ruang yang memiliki 6 sisi berbentuk persegi yang sama besar.\n\nCIRI-CIRI KUBUS:\n1. Memiliki 6 sisi berbentuk persegi\n2. Memiliki 12 rusuk sama panjang\n3. Memiliki 8 titik sudut\n\nRUMUS:\n- Volume = s × s × s = s³\n- Luas Permukaan = 6 × s²\n\nCONTOH:\nJika panjang rusuk kubus = 5 cm, maka:\n- Volume = 5³ = 125 cm³\n- Luas = 6 × 5² = 150 cm²'
                },
                {
                    'judul': 'Balok - Konsep Dasar',
                    'topik': 'balok',
                    'level': 'pemula',
                    'konten': 'BALOK adalah bangun ruang yang memiliki 6 sisi berbentuk persegi panjang.\n\nCIRI-CIRI BALOK:\n1. Memiliki 6 sisi (4 sisi tegak + 2 sisi alas)\n2. Memiliki 12 rusuk\n3. Memiliki 8 titik sudut\n\nRUMUS:\n- Volume = p × l × t\n- Luas Permukaan = 2(pl + pt + lt)\n\nCONTOH:\nBalok dengan p=6cm, l=4cm, t=3cm:\n- Volume = 6×4×3 = 72 cm³\n- Luas = 2(24+18+12) = 108 cm²'
                },
                {
                    'judul': 'Bola - Materi Lengkap',
                    'topik': 'bola',
                    'level': 'menengah',
                    'konten': 'BOLA adalah bangun ruang berbentuk bulat sempurna.\n\nCIRI-CIRI BOLA:\n1. Memiliki 1 sisi melengkung\n2. Tidak memiliki rusuk\n3. Tidak memiliki titik sudut\n\nRUMUS:\n- Volume = 4/3 × π × r³\n- Luas Permukaan = 4 × π × r²\n\nCONTOH:\nBola dengan jari-jari 7 cm:\n- Volume = 4/3 × 22/7 × 7³ ≈ 1437.3 cm³\n- Luas = 4 × 22/7 × 7² = 616 cm²'
                },
                {
                    'judul': 'Tabung - Pendalaman',
                    'topik': 'tabung',
                    'level': 'menengah',
                    'konten': 'TABUNG adalah bangun ruang dengan alas dan tutup berbentuk lingkaran.\n\nCIRI-CIRI:\n1. Memiliki 3 sisi (2 lingkaran + 1 selimut)\n2. Memiliki 2 rusuk lengkung\n\nRUMUS:\n- Volume = π × r² × t\n- Luas Permukaan = 2πr(r + t)\n\nCONTOH:\nTabung r=7cm, t=10cm:\n- Volume = 22/7 × 49 × 10 = 1540 cm³\n- Luas = 2×22/7×7×17 = 748 cm²'
                }
            ]
            
            materials_created = 0
            for mat_data in materials_data:
                existing = TeacherMaterial.query.filter_by(judul=mat_data['judul']).first()
                if not existing:
                    material = TeacherMaterial(
                        judul=mat_data['judul'],
                        topik=mat_data['topik'],
                        konten=mat_data['konten'],
                        level=mat_data['level'],
                        created_by='Pak Budi'
                    )
                    db.session.add(material)
                    materials_created += 1
            
            db.session.commit()
            print(f"   ✅ Created {materials_created} materials")
            
            # 3. Create quiz attempts
            print("🎯 Creating quiz attempts...")
            topics = ['kubus', 'balok', 'bola', 'tabung']
            quiz_count = 0
            
            for student in all_students:
                # Each student takes 3-7 quizzes
                num_quizzes = random.randint(3, 7)
                for _ in range(num_quizzes):
                    quiz = QuizAttempt(
                        user_id=student.id,
                        topik=random.choice(topics),
                        level=student.level,
                        skor=random.randint(40, 100),
                        total_soal=5,
                        benar=random.randint(2, 5),
                        completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                    )
                    db.session.add(quiz)
                    quiz_count += 1
            
            db.session.commit()
            print(f"   ✅ Created {quiz_count} quiz attempts")
            
            # 4. Create emotions
            print("😊 Creating emotion logs...")
            emotion_types = ['cemas', 'bingung', 'netral', 'percaya_diri']
            emotion_count = 0
            
            for student in all_students:
                # Each student logs 5-15 emotions
                num_emotions = random.randint(5, 15)
                for _ in range(num_emotions):
                    emotion = Emotion(
                        user_id=student.id,
                        emosi=random.choice(emotion_types),
                        context=random.choice(topics),
                        waktu=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                    )
                    db.session.add(emotion)
                    emotion_count += 1
            
            db.session.commit()
            print(f"   ✅ Created {emotion_count} emotion logs")
            
            # 5. Create learning logs
            print("📖 Creating learning logs...")
            log_count = 0
            
            for student in all_students:
                # Each student has 5-10 learning sessions
                num_logs = random.randint(5, 10)
                for _ in range(num_logs):
                    topic = random.choice(topics)
                    log = LearningLog(
                        user_id=student.id,
                        materi=f"Belajar {topic.capitalize()}",
                        tipe_aktivitas='belajar',
                        durasi=random.randint(300, 1800),  # 5-30 minutes in seconds
                        waktu=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                    )
                    db.session.add(log)
                    log_count += 1
            
            db.session.commit()
            print(f"   ✅ Created {log_count} learning logs")
            
            print("\n✨ Sample data seeded successfully!")
            print("\n📊 Summary:")
            print(f"   👥 Students: {len(all_students)}")
            print(f"   📚 Materials: {materials_created}")
            print(f"   🎯 Quiz Attempts: {quiz_count}")
            print(f"   😊 Emotions: {emotion_count}")
            print(f"   📖 Learning Logs: {log_count}")
            print("\n🎉 Dashboard should now display real data!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Seeding failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🔐 EMOTIVA-MATH - Sample Data Seeder\n")
    success = seed_sample_data()
    
    if success:
        print("\n✅ Seeding complete!")
        sys.exit(0)
    else:
        print("\n❌ Seeding failed!")
        sys.exit(1)
