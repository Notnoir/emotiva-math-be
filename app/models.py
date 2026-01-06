"""
Database Models untuk EMOTIVA-MATH
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    Model untuk menyimpan learning profile user
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'teacher' or 'student'
    
    # Learning style: visual, auditori, kinestetik (only for students)
    gaya_belajar = db.Column(db.String(20), nullable=True)
    
    # Current level: pemula, menengah, mahir (only for students)
    level = db.Column(db.String(20), default='pemula')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emotions = db.relationship('Emotion', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_logs = db.relationship('LearningLog', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_email=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'nama': self.nama,
            'role': self.role,
            'gaya_belajar': self.gaya_belajar,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def __repr__(self):
        return f'<User {self.nama} ({self.role}) - {self.email}>'


class Emotion(db.Model):
    """
    Model untuk menyimpan emotion logs
    """
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Emotion types: cemas, bingung, netral, percaya_diri
    emosi = db.Column(db.String(20), nullable=False)
    
    # Context: saat belajar materi apa
    context = db.Column(db.String(200))
    
    # Timestamp
    waktu = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emosi': self.emosi,
            'context': self.context,
            'waktu': self.waktu.isoformat() if self.waktu else None
        }
    
    def __repr__(self):
        return f'<Emotion {self.emosi} at {self.waktu}>'


class LearningLog(db.Model):
    """
    Model untuk menyimpan aktivitas learning user
    """
    __tablename__ = 'learning_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Materi yang dipelajari
    materi = db.Column(db.String(100), nullable=False)
    
    # Tipe aktivitas: belajar, latihan, quiz
    tipe_aktivitas = db.Column(db.String(20), default='belajar')
    
    # Skor (jika ada latihan/quiz)
    skor = db.Column(db.Integer, default=0)
    
    # Durasi (dalam detik)
    durasi = db.Column(db.Integer, default=0)
    
    # Timestamp
    waktu = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'materi': self.materi,
            'tipe_aktivitas': self.tipe_aktivitas,
            'skor': self.skor,
            'durasi': self.durasi,
            'waktu': self.waktu.isoformat() if self.waktu else None
        }
    
    def __repr__(self):
        return f'<LearningLog {self.materi} - Score: {self.skor}>'


class TeacherMaterial(db.Model):
    """
    Model untuk menyimpan materi dari GURU
    CRITICAL: Ini adalah SATU-SATUNYA sumber pengetahuan sistem
    """
    __tablename__ = 'teacher_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Judul materi
    judul = db.Column(db.String(200), nullable=False)
    
    # Topik: kubus, balok, bola, tabung, kerucut, limas, prisma
    topik = db.Column(db.String(50), nullable=False)
    
    # Konten lengkap materi dari guru (untuk backward compatibility)
    konten = db.Column(db.Text, nullable=True)
    
    # File path untuk file yang diupload (PDF, DOC, etc)
    file_path = db.Column(db.String(500), nullable=True)
    
    # Original filename
    file_name = db.Column(db.String(255), nullable=True)
    
    # File type/extension
    file_type = db.Column(db.String(50), nullable=True)
    
    # Level: pemula, menengah, mahir
    level = db.Column(db.String(20), default='pemula')
    
    # Pembuat materi (nama guru)
    created_by = db.Column(db.String(100), default='Admin')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'judul': self.judul,
            'topik': self.topik,
            'konten': self.konten,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'level': self.level,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TeacherMaterial {self.judul} - {self.topik}>'


class QuizQuestion(db.Model):
    """
    Model untuk menyimpan soal-soal quiz yang di-generate
    """
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    topik = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    pertanyaan = db.Column(db.Text, nullable=False)
    pilihan_a = db.Column(db.String(500))
    pilihan_b = db.Column(db.String(500))
    pilihan_c = db.Column(db.String(500))
    pilihan_d = db.Column(db.String(500))
    jawaban_benar = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    penjelasan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'topik': self.topik,
            'level': self.level,
            'pertanyaan': self.pertanyaan,
            'pilihan_a': self.pilihan_a,
            'pilihan_b': self.pilihan_b,
            'pilihan_c': self.pilihan_c,
            'pilihan_d': self.pilihan_d,
            'jawaban_benar': self.jawaban_benar,
            'penjelasan': self.penjelasan,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_without_answer(self):
        """Convert to dictionary without revealing correct answer"""
        return {
            'id': self.id,
            'topik': self.topik,
            'level': self.level,
            'pertanyaan': self.pertanyaan,
            'pilihan_a': self.pilihan_a,
            'pilihan_b': self.pilihan_b,
            'pilihan_c': self.pilihan_c,
            'pilihan_d': self.pilihan_d
        }
    
    def __repr__(self):
        return f'<QuizQuestion {self.topik} - {self.level}>'


class QuizAttempt(db.Model):
    """
    Model untuk menyimpan percobaan quiz user
    """
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topik = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    total_soal = db.Column(db.Integer, nullable=False)
    benar = db.Column(db.Integer, default=0)
    salah = db.Column(db.Integer, default=0)
    skor = db.Column(db.Float, nullable=False)  # 0-100
    durasi = db.Column(db.Integer, default=0)  # seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('QuizAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topik': self.topik,
            'level': self.level,
            'total_soal': self.total_soal,
            'benar': self.benar,
            'salah': self.salah,
            'skor': self.skor,
            'durasi': self.durasi,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<QuizAttempt User:{self.user_id} - Score:{self.skor}>'


class QuizAnswer(db.Model):
    """
    Model untuk menyimpan jawaban user per soal
    """
    __tablename__ = 'quiz_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    jawaban_user = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    is_correct = db.Column(db.Boolean, nullable=False)
    waktu_jawab = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'jawaban_user': self.jawaban_user,
            'is_correct': self.is_correct,
            'waktu_jawab': self.waktu_jawab.isoformat() if self.waktu_jawab else None
        }
    
    def __repr__(self):
        return f'<QuizAnswer Q:{self.question_id} - {"✓" if self.is_correct else "✗"}>'
