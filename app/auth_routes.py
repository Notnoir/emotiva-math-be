"""
Authentication Routes untuk Login, Register, dan Verification
"""
from flask import Blueprint, request, jsonify
from app.models import db, User
from app.auth_utils import (
    hash_password, 
    verify_password, 
    generate_jwt_token,
    token_required,
    validate_email,
    validate_password_strength
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user (teacher or student)
    
    Request Body:
        {
            "nama": "string",
            "email": "string",
            "password": "string",
            "role": "teacher" | "student",
            "gaya_belajar": "visual" | "auditori" | "kinestetik" (optional for teacher),
            "level": "pemula" | "menengah" | "mahir" (optional)
        }
    
    Returns:
        {
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "user": {...},
                "token": "jwt_token"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['nama', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Field {field} wajib diisi'
                }), 400
        
        nama = data['nama'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role'].strip().lower()
        
        # Validate role
        if role not in ['teacher', 'student']:
            return jsonify({
                'status': 'error',
                'message': 'Role harus "teacher" atau "student"'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'status': 'error',
                'message': 'Format email tidak valid'
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': 'Email sudah terdaftar. Silakan gunakan email lain atau login.'
            }), 409
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create new user
        new_user = User(
            nama=nama,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        # For students, set learning profile (optional)
        if role == 'student':
            gaya_belajar = data.get('gaya_belajar')  # Can be None
            level = data.get('level')  # Can be None
            
            # Validate gaya_belajar if provided
            if gaya_belajar and gaya_belajar not in ['visual', 'auditori', 'kinestetik']:
                return jsonify({
                    'status': 'error',
                    'message': 'Gaya belajar harus "visual", "auditori", atau "kinestetik"'
                }), 400
            
            # Validate level if provided
            if level and level not in ['pemula', 'menengah', 'mahir']:
                return jsonify({
                    'status': 'error',
                    'message': 'Level harus "pemula", "menengah", atau "mahir"'
                }), 400
            
            # Set values (can be None)
            new_user.gaya_belajar = gaya_belajar if gaya_belajar else None
            new_user.level = level if level else None
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        token = generate_jwt_token(new_user.id, new_user.role)
        
        return jsonify({
            'status': 'success',
            'message': f'{role.capitalize()} berhasil didaftarkan',
            'data': {
                'user': new_user.to_dict(include_email=True),
                'token': token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Registrasi gagal: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user with email and password
    
    Request Body:
        {
            "email": "string",
            "password": "string"
        }
    
    Returns:
        {
            "status": "success",
            "message": "Login berhasil",
            "data": {
                "user": {...},
                "token": "jwt_token"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Email dan password wajib diisi'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Email atau password salah'
            }), 401
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({
                'status': 'error',
                'message': 'Email atau password salah'
            }), 401
        
        # Generate JWT token
        token = generate_jwt_token(user.id, user.role)
        
        return jsonify({
            'status': 'success',
            'message': 'Login berhasil',
            'data': {
                'user': user.to_dict(include_email=True),
                'token': token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login gagal: {str(e)}'
        }), 500


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """
    Verify JWT token and get current user info
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "status": "success",
            "data": {
                "user": {...}
            }
        }
    """
    try:
        # Get user from token (set by @token_required decorator)
        user_id = request.user_id
        
        # Fetch user from database
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User tidak ditemukan'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'user': user.to_dict(include_email=True)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Verifikasi gagal: {str(e)}'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get current logged-in user profile
    Same as verify but more semantic
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "status": "success",
            "data": {
                "user": {...}
            }
        }
    """
    return verify_token()


@auth_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile():
    """
    Update user profile
    Students can update: nama, gaya_belajar, level
    Teachers can update: nama
    
    Request Body:
        {
            "nama": "string" (optional),
            "gaya_belajar": "visual|auditori|kinestetik" (optional, student only),
            "level": "pemula|menengah|mahir" (optional, student only)
        }
    
    Returns:
        {
            "status": "success",
            "message": "Profile updated",
            "data": {
                "user": {...}
            }
        }
    """
    try:
        user_id = request.user_id
        user_role = request.user_role
        data = request.get_json()
        
        # Fetch user
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User tidak ditemukan'
            }), 404
        
        # Update nama if provided
        if 'nama' in data and data['nama']:
            user.nama = data['nama'].strip()
        
        # Students can update learning profile
        if user_role == 'student':
            if 'gaya_belajar' in data and data['gaya_belajar']:
                gaya_belajar = data['gaya_belajar']
                if gaya_belajar not in ['visual', 'auditori', 'kinestetik']:
                    return jsonify({
                        'status': 'error',
                        'message': 'Gaya belajar harus "visual", "auditori", atau "kinestetik"'
                    }), 400
                user.gaya_belajar = gaya_belajar
            
            if 'level' in data and data['level']:
                level = data['level']
                if level not in ['pemula', 'menengah', 'mahir']:
                    return jsonify({
                        'status': 'error',
                        'message': 'Level harus "pemula", "menengah", atau "mahir"'
                    }), 400
                user.level = level
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile berhasil diupdate',
            'data': {
                'user': user.to_dict(include_email=True)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Update profile gagal: {str(e)}'
        }), 500
