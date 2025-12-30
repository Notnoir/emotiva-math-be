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
    
    # Learning style: visual, auditori, kinestetik
    gaya_belajar = db.Column(db.String(20), nullable=False)
    
    # Current level: pemula, menengah, mahir
    level = db.Column(db.String(20), default='pemula')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emotions = db.relationship('Emotion', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_logs = db.relationship('LearningLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'nama': self.nama,
            'gaya_belajar': self.gaya_belajar,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.nama} - {self.gaya_belajar}>'


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
    
    # Konten lengkap materi dari guru
    konten = db.Column(db.Text, nullable=False)
    
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
            'level': self.level,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TeacherMaterial {self.judul} - {self.topik}>'
