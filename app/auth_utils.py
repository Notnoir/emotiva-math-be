"""
Authentication utilities for JWT and password hashing
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'emotiva-math-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        password_hash: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def generate_jwt_token(user_id: int, role: str) -> str:
    """
    Generate JWT token for user
    
    Args:
        user_id: User's database ID
        role: User's role ('teacher' or 'student')
        
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload


def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    Usage: @token_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'status': 'error',
                    'message': 'Token format invalid. Use: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token tidak ditemukan. Silakan login terlebih dahulu.'
            }), 401
        
        try:
            # Decode token
            payload = decode_jwt_token(token)
            current_user_id = payload['user_id']
            current_user_role = payload['role']
            
            # Add user info to request context
            request.user_id = current_user_id
            request.user_role = current_user_role
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'status': 'error',
                'message': 'Token sudah expired. Silakan login kembali.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'status': 'error',
                'message': 'Token tidak valid.'
            }), 401
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error validasi token: {str(e)}'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(*allowed_roles):
    """
    Decorator to restrict access by role
    Usage: @role_required('teacher', 'student')
    
    Args:
        allowed_roles: Roles that are allowed to access the route
    """
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            if request.user_role not in allowed_roles:
                return jsonify({
                    'status': 'error',
                    'message': f'Akses ditolak. Role {request.user_role} tidak diizinkan untuk endpoint ini.'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_email(email: str) -> bool:
    """
    Simple email validation
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password harus minimal 6 karakter"
    
    if len(password) > 100:
        return False, "Password terlalu panjang (maksimal 100 karakter)"
    
    return True, ""
