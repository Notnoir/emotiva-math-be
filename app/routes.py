from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import db, User, Emotion, LearningLog, TeacherMaterial, QuizQuestion, QuizAttempt, QuizAnswer
from app.ai_engine import adaptive_engine
from app.llm_service import llm_service
from app.auth_utils import token_required, role_required

# Blueprint untuk API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint untuk health check
    GET /api/health
    
    Returns:
        JSON response dengan status aplikasi
    """
    return jsonify({
        'status': 'healthy',
        'message': 'EMOTIVA-MATH API is running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/api/health',
            'profile': '/api/profile [GET, POST]',
            'profile_detail': '/api/profile/<id> [GET, PUT]',
            'emotion': '/api/emotion [POST]',
            'emotion_history': '/api/emotion/<user_id> [GET]',
            'learning_logs': '/api/learning-logs/<user_id> [GET, POST]',
            'materials': '/api/materials [GET, POST]',
            'materials_detail': '/api/materials/<id> [GET, PUT, DELETE]',
            'materials_search': '/api/materials/search?q=keyword [GET]',
            'adaptive_content': '/api/adaptive/content [POST]',
            'recommendations': '/api/recommendations/<user_id> [GET]',
            'visualization': '/api/visualization/generate [POST]',
            'quiz_generate': '/api/quiz/generate [POST]',
            'quiz_submit': '/api/quiz/submit [POST]',
            'quiz_history': '/api/quiz/history/<user_id> [GET]',
            'quiz_stats': '/api/quiz/stats/<user_id> [GET]',
            'dashboard_overview': '/api/dashboard/overview [GET]',
            'dashboard_students': '/api/dashboard/students [GET]',
            'dashboard_topics': '/api/dashboard/topics [GET]',
            'dashboard_emotions': '/api/dashboard/emotions [GET]',
            'dashboard_performance': '/api/dashboard/performance [GET]'
        }
    }), 200

@api_bp.route('/info', methods=['GET'])
def get_info():
    """
    Endpoint untuk informasi sistem
    GET /api/info
    
    Returns:
        JSON response dengan informasi sistem
    """
    return jsonify({
        'status': 'success',
        'data': {
            'app_name': 'EMOTIVA-MATH',
            'full_name': 'Emotion-Aware Adaptive Mathematics Learning System',
            'version': '1.0.0-beta',
            'topic': 'Bangun Ruang (3D Shapes)',
            'features': [
                'Learning Style Detection',
                'Emotion-Aware Learning',
                'Adaptive Content Delivery',
                'AR/3D Visualization',
                'Personalized Exercises'
            ],
            'status': 'In Development - Phase 2 Complete'
        }
    }), 200

# ==================== PROFILE ENDPOINTS ====================

@api_bp.route('/profile', methods=['GET', 'POST'])
def handle_profiles():
    """
    GET /api/profile - Get all profiles
    POST /api/profile - Create new profile
    """
    if request.method == 'GET':
        # Get all users
        users = User.query.all()
        return jsonify({
            'status': 'success',
            'count': len(users),
            'data': [user.to_dict() for user in users]
        }), 200
    
    elif request.method == 'POST':
        # Create new user profile
        data = request.get_json()
        
        # Validation
        if not data or 'nama' not in data or 'gaya_belajar' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: nama, gaya_belajar'
            }), 400
        
        # Validate gaya_belajar
        valid_styles = ['visual', 'auditori', 'kinestetik']
        if data['gaya_belajar'] not in valid_styles:
            return jsonify({
                'status': 'error',
                'message': f'Invalid gaya_belajar. Must be one of: {valid_styles}'
            }), 400
        
        # Create user
        user = User(
            nama=data['nama'],
            gaya_belajar=data['gaya_belajar'],
            level=data.get('level', 'pemula')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile created successfully',
            'data': user.to_dict()
        }), 201

@api_bp.route('/profile/<int:user_id>', methods=['GET', 'PUT'])
def handle_profile_detail(user_id):
    """
    GET /api/profile/<id> - Get specific profile
    PUT /api/profile/<id> - Update profile
    """
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'User with id {user_id} not found'
        }), 404
    
    if request.method == 'GET':
        # Get user detail with stats
        emotion_count = len(user.emotions)
        learning_count = len(user.learning_logs)
        
        user_data = user.to_dict()
        user_data['stats'] = {
            'total_emotions_logged': emotion_count,
            'total_learning_activities': learning_count
        }
        
        return jsonify({
            'status': 'success',
            'data': user_data
        }), 200
    
    elif request.method == 'PUT':
        # Update user profile
        data = request.get_json()
        
        if 'nama' in data:
            user.nama = data['nama']
        if 'gaya_belajar' in data:
            valid_styles = ['visual', 'auditori', 'kinestetik']
            if data['gaya_belajar'] in valid_styles:
                user.gaya_belajar = data['gaya_belajar']
        if 'level' in data:
            valid_levels = ['pemula', 'menengah', 'mahir']
            if data['level'] in valid_levels:
                user.level = data['level']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'data': user.to_dict()
        }), 200

# ==================== EMOTION ENDPOINTS ====================

@api_bp.route('/emotion', methods=['POST'])
def log_emotion():
    """
    POST /api/emotion - Log emotion
    
    Body:
        {
            "user_id": int,
            "emosi": string,
            "context": string (optional)
        }
    """
    data = request.get_json()
    
    # Validation
    if not data or 'user_id' not in data or 'emosi' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: user_id, emosi'
        }), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'User with id {data["user_id"]} not found'
        }), 404
    
    # Validate emotion type
    valid_emotions = ['cemas', 'bingung', 'netral', 'percaya_diri']
    if data['emosi'] not in valid_emotions:
        return jsonify({
            'status': 'error',
            'message': f'Invalid emotion. Must be one of: {valid_emotions}'
        }), 400
    
    # Create emotion log
    emotion = Emotion(
        user_id=data['user_id'],
        emosi=data['emosi'],
        context=data.get('context', '')
    )
    
    db.session.add(emotion)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Emotion logged successfully',
        'data': emotion.to_dict()
    }), 201

@api_bp.route('/emotion/<int:user_id>', methods=['GET'])
def get_emotion_history(user_id):
    """
    GET /api/emotion/<user_id> - Get emotion history
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'User with id {user_id} not found'
        }), 404
    
    emotions = Emotion.query.filter_by(user_id=user_id).order_by(Emotion.waktu.desc()).all()
    
    return jsonify({
        'status': 'success',
        'count': len(emotions),
        'data': [emotion.to_dict() for emotion in emotions]
    }), 200

# ==================== LEARNING LOG ENDPOINTS ====================

@api_bp.route('/learning-logs/<int:user_id>', methods=['GET', 'POST'])
def handle_learning_logs(user_id):
    """
    GET /api/learning-logs/<user_id> - Get learning logs
    POST /api/learning-logs/<user_id> - Create learning log
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'User with id {user_id} not found'
        }), 404
    
    if request.method == 'GET':
        logs = LearningLog.query.filter_by(user_id=user_id).order_by(LearningLog.waktu.desc()).all()
        
        return jsonify({
            'status': 'success',
            'count': len(logs),
            'data': [log.to_dict() for log in logs]
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validation
        if not data or 'materi' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: materi'
            }), 400
        
        # Create learning log
        log = LearningLog(
            user_id=user_id,
            materi=data['materi'],
            tipe_aktivitas=data.get('tipe_aktivitas', 'belajar'),
            skor=data.get('skor', 0),
            durasi=data.get('durasi', 0)
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Learning log created successfully',
            'data': log.to_dict()
        }), 201

@api_bp.route('/test', methods=['POST'])
def test_endpoint():
    """
    Endpoint untuk testing POST request
    POST /api/test
    
    Accepts:
        JSON body dengan data apapun
    
    Returns:
        Echo data yang dikirim
    """
    data = request.get_json()
    
    return jsonify({
        'status': 'success',
        'message': 'POST request received',
        'received_data': data,
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== ADAPTIVE LEARNING ENDPOINTS ====================

@api_bp.route('/adaptive/content', methods=['POST'])
@token_required
def get_adaptive_content():
    """
    POST /api/adaptive/content - Get adaptive learning content (Authenticated users)
    
    Body:
        {
            "user_id": int,
            "topic": string (kubus, balok, etc),
            "emotion": string (optional - will use latest if not provided)
        }
    
    Returns:
        Personalized learning content based on user profile, emotion, and performance
    """
    data = request.get_json()
    
    # Validation
    if not data or 'user_id' not in data or 'topic' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: user_id, topic'
        }), 400
    
    # Get user profile
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'User with id {data["user_id"]} not found'
        }), 404
    
    # Get current emotion (from request or latest emotion log)
    emotion = data.get('emosi', None)
    if not emotion:
        latest_emotion = Emotion.query.filter_by(user_id=user.id).order_by(Emotion.waktu.desc()).first()
        emotion = latest_emotion.emosi if latest_emotion else 'netral'
    
    # Get previous scores for adaptive difficulty
    learning_logs = LearningLog.query.filter_by(
        user_id=user.id,
        tipe_aktivitas='quiz'
    ).order_by(LearningLog.waktu.desc()).limit(5).all()
    
    previous_scores = [log.skor for log in learning_logs if log.skor > 0]
    
    # Generate adaptive content using AI engine
    try:
        adaptive_content = adaptive_engine.generate_content(
            topic=data['topic'],
            learning_style=user.gaya_belajar,
            emotion=emotion,
            level=user.level,
            previous_scores=previous_scores
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Adaptive content generated successfully',
            'data': adaptive_content,
            'user_context': {
                'nama': user.nama,
                'gaya_belajar': user.gaya_belajar,
                'level': user.level,
                'current_emotion': emotion,
                'average_score': sum(previous_scores) / len(previous_scores) if previous_scores else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating adaptive content: {str(e)}'
        }), 500

# ==================== TEACHER MATERIALS ENDPOINTS ====================
# CRITICAL: Ini adalah sumber pengetahuan UTAMA sistem

@api_bp.route('/materials', methods=['GET', 'POST'])
@token_required
def handle_materials():
    """
    GET /api/materials - Get all materials (authenticated users)
    POST /api/materials - Upload materi baru (TEACHER ONLY)
    
    Query params untuk GET:
        - topik: string (opsional)
        - level: string (opsional)
    
    Body untuk POST:
        {
            "judul": string,
            "topik": string (kubus, balok, bola, tabung, kerucut, limas, prisma),
            "konten": string (materi lengkap),
            "level": string (pemula, menengah, mahir)
        }
    """
    if request.method == 'GET':
        # Get materials dengan optional filtering
        topik = request.args.get('topik')
        level = request.args.get('level')
        
        query = TeacherMaterial.query
        
        if topik:
            query = query.filter_by(topik=topik.lower())
        if level:
            query = query.filter_by(level=level.lower())
        
        materials = query.order_by(TeacherMaterial.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'count': len(materials),
            'data': [material.to_dict() for material in materials]
        }), 200
    
    elif request.method == 'POST':
        # Only teachers can create materials
        if request.user_role != 'teacher':
            return jsonify({
                'status': 'error',
                'message': 'Akses ditolak. Hanya guru yang dapat mengunggah materi.'
            }), 403
        
        # Create new material
        data = request.get_json()
        
        # Validation
        required_fields = ['judul', 'topik', 'konten']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate topik
        valid_topics = ['kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma']
        if data['topik'].lower() not in valid_topics:
            return jsonify({
                'status': 'error',
                'message': f'Invalid topik. Must be one of: {valid_topics}'
            }), 400
        
        # Validate level (if provided)
        level = data.get('level', 'pemula').lower()
        valid_levels = ['pemula', 'menengah', 'mahir']
        if level not in valid_levels:
            return jsonify({
                'status': 'error',
                'message': f'Invalid level. Must be one of: {valid_levels}'
            }), 400
        
        # Get teacher info from token
        teacher = User.query.get(request.user_id)
        created_by = teacher.nama if teacher else 'Unknown'
        
        # Create material
        material = TeacherMaterial(
            judul=data['judul'],
            topik=data['topik'].lower(),
            konten=data['konten'],
            level=level,
            created_by=created_by,
            teacher_id=request.user_id
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Material uploaded successfully',
            'data': material.to_dict()
        }), 201

@api_bp.route('/materials/<int:material_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_material_detail(material_id):
    """
    GET /api/materials/<id> - Get specific material (authenticated users)
    PUT /api/materials/<id> - Update material (TEACHER ONLY)
    DELETE /api/materials/<id> - Delete material (TEACHER ONLY)
    """
    material = TeacherMaterial.query.get(material_id)
    
    if not material:
        return jsonify({
            'status': 'error',
            'message': f'Material with id {material_id} not found'
        }), 404
    
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'data': material.to_dict()
        }), 200
    
    elif request.method == 'PUT':
        # Only teachers can update materials
        if request.user_role != 'teacher':
            return jsonify({
                'status': 'error',
                'message': 'Akses ditolak. Hanya guru yang dapat mengupdate materi.'
            }), 403
        
        data = request.get_json()
        
        # Update fields
        if 'judul' in data:
            material.judul = data['judul']
        if 'topik' in data:
            valid_topics = ['kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma']
            if data['topik'].lower() in valid_topics:
                material.topik = data['topik'].lower()
        if 'konten' in data:
            material.konten = data['konten']
        if 'level' in data:
            valid_levels = ['pemula', 'menengah', 'mahir']
            if data['level'].lower() in valid_levels:
                material.level = data['level'].lower()
        
        material.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Material updated successfully',
            'data': material.to_dict()
        }), 200
    
    elif request.method == 'DELETE':
        # Only teachers can delete materials
        if request.user_role != 'teacher':
            return jsonify({
                'status': 'error',
                'message': 'Akses ditolak. Hanya guru yang dapat menghapus materi.'
            }), 403
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Material deleted successfully'
        }), 200

@api_bp.route('/materials/search', methods=['GET'])
def search_materials():
    """
    GET /api/materials/search - Cari materi berdasarkan keyword
    
    Query params:
        - q: string (keyword untuk search)
        - topik: string (opsional filter)
        - level: string (opsional filter)
    """
    keyword = request.args.get('q', '')
    topik = request.args.get('topik')
    level = request.args.get('level')
    
    if not keyword:
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameter: q (keyword)'
        }), 400
    
    query = TeacherMaterial.query
    
    # Search in judul or konten
    search_filter = db.or_(
        TeacherMaterial.judul.contains(keyword),
        TeacherMaterial.konten.contains(keyword)
    )
    query = query.filter(search_filter)
    
    # Apply additional filters
    if topik:
        query = query.filter_by(topik=topik.lower())
    if level:
        query = query.filter_by(level=level.lower())
    
    materials = query.order_by(TeacherMaterial.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'keyword': keyword,
        'count': len(materials),
        'data': [material.to_dict() for material in materials]
    }), 200

# ==================== RECOMMENDATION ENDPOINT ====================

@api_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    GET /api/recommendations/<user_id> - Get recommended learning topics
    """
    if not user_id:
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameter: user_id'
        }), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'User with id {user_id} not found'
        }), 404
    
    # Get learning history
    completed_topics = db.session.query(LearningLog.materi).filter_by(
        user_id=user_id
    ).distinct().all()
    
    completed_topics_list = [topic[0] for topic in completed_topics]
    
    # Simple recommendation logic
    all_topics = ['kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas']
    recommended_topics = [t for t in all_topics if t not in [ct.lower() for ct in completed_topics_list]]
    
    return jsonify({
        'status': 'success',
        'data': {
            'user_id': user_id,
            'level': user.level,
            'gaya_belajar': user.gaya_belajar,
            'completed_topics': completed_topics_list,
            'recommended_topics': recommended_topics[:3],  # Top 3 recommendations
            'total_completed': len(completed_topics_list)
        }
    }), 200

# ==================== VISUALIZATION ENDPOINTS ====================

@api_bp.route('/visualization/generate', methods=['POST'])
def generate_visualization():
    """
    POST /api/visualization/generate - Generate 3D visualization JSON
    
    CRITICAL: LLM generates DECLARATIVE JSON only, NOT JavaScript code
    
    Body:
        {
            "topic": string (kubus, balok, bola, tabung, kerucut, limas),
            "difficulty": string (optional - pemula, menengah, mahir),
            "context": string (optional - konteks tambahan)
        }
    
    Returns:
        Declarative JSON untuk di-render oleh frontend
    """
    data = request.get_json()
    
    # Validation
    if not data or 'topic' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required field: topic'
        }), 400
    
    topic = data['topic'].lower()
    valid_topics = ['kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma']
    
    if topic not in valid_topics:
        return jsonify({
            'status': 'error',
            'message': f'Invalid topic. Must be one of: {valid_topics}'
        }), 400
    
    difficulty = data.get('difficulty', 'pemula')
    context = data.get('context', None)
    
    # Try LLM first
    if llm_service.is_available():
        viz_json = llm_service.generate_visualization_json(
            topic=topic,
            difficulty=difficulty,
            context=context
        )
        
        if viz_json:
            return jsonify({
                'status': 'success',
                'message': 'Visualization JSON generated',
                'source': 'llm',
                'data': viz_json
            }), 200
    
    # Fallback: Rule-based JSON generation
    fallback_json = _generate_fallback_visualization(topic)
    
    return jsonify({
        'status': 'success',
        'message': 'Visualization JSON generated (fallback)',
        'source': 'rule-based',
        'data': fallback_json
    }), 200

def _generate_fallback_visualization(topic: str) -> dict:
    """
    Generate simple fallback visualization JSON (rule-based)
    Digunakan jika LLM tidak tersedia
    """
    base_visualizations = {
        'kubus': {
            'type': 'visualization',
            'title': 'Kubus',
            'description': 'Bangun ruang dengan 6 sisi persegi sama besar',
            'objects': [
                {
                    'id': 'kubus1',
                    'type': 'box',
                    'color': '#4F46E5',
                    'position': [0, 0, 0],
                    'scale': [2, 2, 2],
                    'rotation': [0, 0, 0],
                    'wireframe': False,
                    'label': 'Kubus',
                    'opacity': 0.9
                }
            ],
            'camera': {
                'position': [5, 5, 5],
                'lookAt': [0, 0, 0]
            },
            'annotations': [
                {
                    'text': 's = panjang rusuk',
                    'position': [2, 2, 0],
                    'color': '#EF4444'
                }
            ],
            'animation': {
                'rotate': True,
                'speed': 0.5
            }
        },
        'balok': {
            'type': 'visualization',
            'title': 'Balok',
            'description': 'Bangun ruang dengan 6 sisi persegi panjang',
            'objects': [
                {
                    'id': 'balok1',
                    'type': 'box',
                    'color': '#10B981',
                    'position': [0, 0, 0],
                    'scale': [3, 2, 1.5],
                    'rotation': [0, 0, 0],
                    'wireframe': False,
                    'label': 'Balok',
                    'opacity': 0.9
                }
            ],
            'camera': {
                'position': [5, 4, 5],
                'lookAt': [0, 0, 0]
            },
            'annotations': [
                {
                    'text': 'p × l × t',
                    'position': [2, 1.5, 0],
                    'color': '#F59E0B'
                }
            ],
            'animation': {
                'rotate': True,
                'speed': 0.5
            }
        },
        'bola': {
            'type': 'visualization',
            'title': 'Bola',
            'description': 'Bangun ruang berbentuk bulat sempurna',
            'objects': [
                {
                    'id': 'bola1',
                    'type': 'sphere',
                    'color': '#EC4899',
                    'position': [0, 0, 0],
                    'scale': [1.5, 1.5, 1.5],
                    'rotation': [0, 0, 0],
                    'wireframe': False,
                    'label': 'Bola',
                    'opacity': 0.9
                }
            ],
            'camera': {
                'position': [4, 3, 4],
                'lookAt': [0, 0, 0]
            },
            'annotations': [
                {
                    'text': 'r = jari-jari',
                    'position': [1.5, 0, 0],
                    'color': '#8B5CF6'
                }
            ],
            'animation': {
                'rotate': True,
                'speed': 0.3
            }
        },
        'tabung': {
            'type': 'visualization',
            'title': 'Tabung',
            'description': 'Bangun ruang dengan alas dan tutup lingkaran',
            'objects': [
                {
                    'id': 'tabung1',
                    'type': 'cylinder',
                    'color': '#F59E0B',
                    'position': [0, 0, 0],
                    'scale': [1.2, 3, 1.2],
                    'rotation': [0, 0, 0],
                    'wireframe': False,
                    'label': 'Tabung',
                    'opacity': 0.9
                }
            ],
            'camera': {
                'position': [5, 3, 5],
                'lookAt': [0, 0, 0]
            },
            'annotations': [
                {
                    'text': 't = tinggi',
                    'position': [2, 1.5, 0],
                    'color': '#EF4444'
                },
                {
                    'text': 'r = jari-jari',
                    'position': [1.5, -1.5, 0],
                    'color': '#3B82F6'
                }
            ],
            'animation': {
                'rotate': True,
                'speed': 0.4
            }
        },
        'kerucut': {
            'type': 'visualization',
            'title': 'Kerucut',
            'description': 'Bangun ruang dengan alas lingkaran dan puncak',
            'objects': [
                {
                    'id': 'kerucut1',
                    'type': 'cone',
                    'color': '#8B5CF6',
                    'position': [0, 0, 0],
                    'scale': [1.5, 3, 1.5],
                    'rotation': [0, 0, 0],
                    'wireframe': False,
                    'label': 'Kerucut',
                    'opacity': 0.9
                }
            ],
            'camera': {
                'position': [5, 3, 5],
                'lookAt': [0, 0, 0]
            },
            'annotations': [
                {
                    'text': 't = tinggi',
                    'position': [0, 3, 0],
                    'color': '#EF4444'
                },
                {
                    'text': 'r = jari-jari alas',
                    'position': [1.5, -1.5, 0],
                    'color': '#10B981'
                }
            ],
            'animation': {
                'rotate': True,
                'speed': 0.4
            }
        },
        'limas': {
            'type': 'visualization',
            'title': 'Limas Segiempat',
            'description': 'Bangun ruang dengan alas segiempat dan puncak',
            'objects': [
                {
                    'id': 'limas1',
                    'type': 'cone',
                    'color': '#EF4444',
                    'position': [0, 0, 0],
                    'scale': [2, 3, 2],
                    'rotation': [0, 0, 0],
                    'wireframe': False,
                    'label': 'Limas',
                    'opacity': 0.9
                }
            ],
            'camera': {
                'position': [6, 4, 6],
                'lookAt': [0, 0, 0]
            },
            'annotations': [
                {
                    'text': 'Puncak limas',
                    'position': [0, 3, 0],
                    'color': '#8B5CF6'
                }
            ],
            'animation': {
                'rotate': True,
                'speed': 0.4
            }
        }
    }
    
    return base_visualizations.get(topic, base_visualizations['kubus'])

# ==================== QUIZ ENDPOINTS ====================

@api_bp.route('/quiz/generate', methods=['POST'])
@token_required
def generate_quiz():
    """
    Generate quiz questions for a topic (Authenticated users)
    POST /api/quiz/generate
    Body: {"topik": "kubus", "level": "pemula", "num_questions": 5}
    """
    try:
        data = request.get_json()
        topik = data.get('topik', 'kubus')
        level = data.get('level', 'pemula')
        num_questions = data.get('num_questions', 5)
        
        # Validate input
        valid_topics = ['kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma']
        valid_levels = ['pemula', 'menengah', 'mahir']
        
        if topik not in valid_topics:
            return jsonify({
                'status': 'error',
                'message': f'Invalid topic. Must be one of: {", ".join(valid_topics)}'
            }), 400
        
        if level not in valid_levels:
            return jsonify({
                'status': 'error',
                'message': f'Invalid level. Must be one of: {", ".join(valid_levels)}'
            }), 400
        
        if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 10:
            return jsonify({
                'status': 'error',
                'message': 'num_questions must be between 1 and 10'
            }), 400
        
        # Generate questions using LLM
        questions = llm_service.generate_quiz_questions(topik, level, num_questions)
        
        if not questions:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate questions. Please check teacher materials exist for this topic.'
            }), 500
        
        # Save questions to database
        saved_questions = []
        for q_data in questions:
            question = QuizQuestion(
                topik=topik,
                level=level,
                pertanyaan=q_data['pertanyaan'],
                pilihan_a=q_data['pilihan_a'],
                pilihan_b=q_data['pilihan_b'],
                pilihan_c=q_data['pilihan_c'],
                pilihan_d=q_data['pilihan_d'],
                jawaban_benar=q_data['jawaban_benar'],
                penjelasan=q_data['penjelasan']
            )
            db.session.add(question)
            db.session.flush()  # Get ID before commit
            saved_questions.append(question.to_dict_without_answer())
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Generated {len(saved_questions)} questions',
            'data': {
                'topik': topik,
                'level': level,
                'questions': saved_questions
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Quiz generation failed: {str(e)}'
        }), 500


@api_bp.route('/quiz/submit', methods=['POST'])
@token_required
def submit_quiz():
    """
    Submit quiz answers and get score (Authenticated users)
    POST /api/quiz/submit
    Body: {
        "user_id": 1,
        "topik": "kubus",
        "level": "pemula",
        "answers": [
            {"question_id": 1, "jawaban": "A"},
            {"question_id": 2, "jawaban": "B"}
        ],
        "durasi": 120
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        topik = data.get('topik')
        level = data.get('level')
        answers = data.get('answers', [])
        durasi = data.get('durasi', 0)
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': f'User {user_id} not found'
            }), 404
        
        if not answers:
            return jsonify({
                'status': 'error',
                'message': 'No answers provided'
            }), 400
        
        # Grade answers
        total_soal = len(answers)
        benar = 0
        salah = 0
        graded_answers = []
        
        for ans in answers:
            question_id = ans.get('question_id')
            jawaban_user = ans.get('jawaban', '').upper()
            
            # Get correct answer
            question = QuizQuestion.query.get(question_id)
            if not question:
                continue
            
            is_correct = (jawaban_user == question.jawaban_benar)
            if is_correct:
                benar += 1
            else:
                salah += 1
            
            graded_answers.append({
                'question_id': question_id,
                'jawaban_user': jawaban_user,
                'jawaban_benar': question.jawaban_benar,
                'is_correct': is_correct,
                'pertanyaan': question.pertanyaan,
                'penjelasan': question.penjelasan
            })
        
        # Calculate score
        skor = (benar / total_soal * 100) if total_soal > 0 else 0
        
        # Save attempt
        attempt = QuizAttempt(
            user_id=user_id,
            topik=topik,
            level=level,
            total_soal=total_soal,
            benar=benar,
            salah=salah,
            skor=skor,
            durasi=durasi
        )
        db.session.add(attempt)
        db.session.flush()
        
        # Save individual answers
        for ans in graded_answers:
            quiz_answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=ans['question_id'],
                jawaban_user=ans['jawaban_user'],
                is_correct=ans['is_correct']
            )
            db.session.add(quiz_answer)
        
        db.session.commit()
        
        # Log learning activity
        learning_log = LearningLog(
            user_id=user_id,
            materi=f'Quiz {topik}',
            tipe_aktivitas='quiz',
            skor=int(skor),
            durasi=durasi
        )
        db.session.add(learning_log)
        db.session.commit()
        
        # Provide feedback based on score
        if skor >= 80:
            feedback = "Luar biasa! Pemahaman Anda sangat baik! 🎉"
            next_step = "Coba tingkatkan ke level berikutnya!"
        elif skor >= 60:
            feedback = "Bagus! Anda sudah memahami konsep dasar. 👍"
            next_step = "Coba pelajari lagi bagian yang masih kurang."
        else:
            feedback = "Tetap semangat! Pelajari materi lagi ya. 💪"
            next_step = "Review materi dan coba latihan lagi."
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz submitted successfully',
            'data': {
                'attempt_id': attempt.id,
                'total_soal': total_soal,
                'benar': benar,
                'salah': salah,
                'skor': round(skor, 2),
                'durasi': durasi,
                'feedback': feedback,
                'next_step': next_step,
                'answers': graded_answers
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Quiz submission failed: {str(e)}'
        }), 500


@api_bp.route('/quiz/history/<int:user_id>', methods=['GET'])
@token_required
def get_quiz_history(user_id):
    """
    Get quiz history for a user (Authenticated users)
    GET /api/quiz/history/<user_id>
    Query params: ?topik=kubus&limit=10
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': f'User {user_id} not found'
            }), 404
        
        # Get query parameters
        topik = request.args.get('topik')
        limit = request.args.get('limit', 10, type=int)
        
        # Build query
        query = QuizAttempt.query.filter_by(user_id=user_id)
        
        if topik:
            query = query.filter_by(topik=topik)
        
        # Get attempts ordered by date
        attempts = query.order_by(QuizAttempt.completed_at.desc()).limit(limit).all()
        
        # Calculate stats
        if attempts:
            avg_skor = sum(a.skor for a in attempts) / len(attempts)
            best_skor = max(a.skor for a in attempts)
            total_attempts = len(attempts)
        else:
            avg_skor = 0
            best_skor = 0
            total_attempts = 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user_id,
                'total_attempts': total_attempts,
                'avg_skor': round(avg_skor, 2),
                'best_skor': round(best_skor, 2),
                'attempts': [a.to_dict() for a in attempts]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get quiz history: {str(e)}'
        }), 500


@api_bp.route('/quiz/stats/<int:user_id>', methods=['GET'])
@token_required
def get_quiz_stats(user_id):
    """
    Get detailed quiz statistics for a user (Authenticated users)
    GET /api/quiz/stats/<user_id>
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': f'User {user_id} not found'
            }), 404
        
        # Get all attempts
        attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        
        if not attempts:
            return jsonify({
                'status': 'success',
                'data': {
                    'user_id': user_id,
                    'total_attempts': 0,
                    'stats_by_topic': {},
                    'stats_by_level': {},
                    'overall': {
                        'avg_skor': 0,
                        'best_skor': 0,
                        'total_questions': 0,
                        'total_correct': 0
                    }
                }
            }), 200
        
        # Stats by topic
        stats_by_topic = {}
        stats_by_level = {}
        total_correct = 0
        total_questions = 0
        
        for attempt in attempts:
            # By topic
            if attempt.topik not in stats_by_topic:
                stats_by_topic[attempt.topik] = {
                    'attempts': 0,
                    'avg_skor': 0,
                    'best_skor': 0,
                    'scores': []
                }
            stats_by_topic[attempt.topik]['attempts'] += 1
            stats_by_topic[attempt.topik]['scores'].append(attempt.skor)
            
            # By level
            if attempt.level not in stats_by_level:
                stats_by_level[attempt.level] = {
                    'attempts': 0,
                    'avg_skor': 0,
                    'best_skor': 0,
                    'scores': []
                }
            stats_by_level[attempt.level]['attempts'] += 1
            stats_by_level[attempt.level]['scores'].append(attempt.skor)
            
            # Overall
            total_correct += attempt.benar
            total_questions += attempt.total_soal
        
        # Calculate averages
        for topic in stats_by_topic:
            scores = stats_by_topic[topic]['scores']
            stats_by_topic[topic]['avg_skor'] = round(sum(scores) / len(scores), 2)
            stats_by_topic[topic]['best_skor'] = round(max(scores), 2)
            del stats_by_topic[topic]['scores']
        
        for level in stats_by_level:
            scores = stats_by_level[level]['scores']
            stats_by_level[level]['avg_skor'] = round(sum(scores) / len(scores), 2)
            stats_by_level[level]['best_skor'] = round(max(scores), 2)
            del stats_by_level[level]['scores']
        
        all_scores = [a.skor for a in attempts]
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user_id,
                'total_attempts': len(attempts),
                'stats_by_topic': stats_by_topic,
                'stats_by_level': stats_by_level,
                'overall': {
                    'avg_skor': round(sum(all_scores) / len(all_scores), 2),
                    'best_skor': round(max(all_scores), 2),
                    'total_questions': total_questions,
                    'total_correct': total_correct,
                    'accuracy': round((total_correct / total_questions * 100), 2) if total_questions > 0 else 0
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get quiz stats: {str(e)}'
        }), 500


# ==================== ERROR HANDLERS ====================# ==================== TEACHER DASHBOARD ANALYTICS ====================

@api_bp.route('/dashboard/overview', methods=['GET'])
@role_required('teacher')
def get_dashboard_overview():
    """
    Get overview statistics for teacher dashboard (TEACHER ONLY)
    GET /api/dashboard/overview
    """
    try:
        # Total users
        total_users = User.query.count()
        
        # Total materials
        total_materials = TeacherMaterial.query.count()
        
        # Total quiz attempts
        total_quizzes = QuizAttempt.query.count()
        
        # Total learning activities
        total_activities = LearningLog.query.count()
        
        # Average quiz score
        quiz_scores = db.session.query(QuizAttempt.skor).all()
        avg_quiz_score = sum(s[0] for s in quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_activities = LearningLog.query.filter(LearningLog.waktu >= week_ago).count()
        recent_quizzes = QuizAttempt.query.filter(QuizAttempt.completed_at >= week_ago).count()
        
        # User distribution by level
        level_distribution = db.session.query(
            User.level, 
            db.func.count(User.id)
        ).group_by(User.level).all()
        
        level_stats = {level: count for level, count in level_distribution}
        
        # User distribution by learning style
        style_distribution = db.session.query(
            User.gaya_belajar,
            db.func.count(User.id)
        ).group_by(User.gaya_belajar).all()
        
        style_stats = {style: count for style, count in style_distribution}
        
        # Materials by topic
        material_distribution = db.session.query(
            TeacherMaterial.topik,
            db.func.count(TeacherMaterial.id)
        ).group_by(TeacherMaterial.topik).all()
        
        material_stats = {topik: count for topik, count in material_distribution}
        
        return jsonify({
            'status': 'success',
            'data': {
                'overview': {
                    'total_users': total_users,
                    'total_materials': total_materials,
                    'total_quizzes': total_quizzes,
                    'total_activities': total_activities,
                    'avg_quiz_score': round(avg_quiz_score, 2)
                },
                'recent_activity': {
                    'last_7_days_activities': recent_activities,
                    'last_7_days_quizzes': recent_quizzes
                },
                'distributions': {
                    'by_level': level_stats,
                    'by_learning_style': style_stats,
                    'materials_by_topic': material_stats
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get dashboard overview: {str(e)}'
        }), 500


@api_bp.route('/dashboard/students', methods=['GET'])
@role_required('teacher')
def get_student_analytics():
    """
    Get detailed student analytics (TEACHER ONLY)
    GET /api/dashboard/students
    Query params: ?limit=10&sort=score
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        sort_by = request.args.get('sort', 'recent')  # recent, score, activity
        
        users = User.query.all()
        student_data = []
        
        for user in users:
            # Get quiz attempts
            quiz_attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
            total_quizzes = len(quiz_attempts)
            avg_score = sum(q.skor for q in quiz_attempts) / total_quizzes if total_quizzes > 0 else 0
            
            # Get learning activities
            activities = LearningLog.query.filter_by(user_id=user.id).all()
            total_activities = len(activities)
            total_duration = sum(a.durasi for a in activities)
            
            # Get emotions
            emotions = Emotion.query.filter_by(user_id=user.id).all()
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion.emosi] = emotion_counts.get(emotion.emosi, 0) + 1
            
            # Dominant emotion
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'netral'
            
            # Last activity
            last_activity = activities[-1].waktu if activities else None
            
            student_data.append({
                'id': user.id,
                'nama': user.nama,
                'level': user.level,
                'gaya_belajar': user.gaya_belajar,
                'total_quizzes': total_quizzes,
                'avg_quiz_score': round(avg_score, 2),
                'total_activities': total_activities,
                'total_duration_minutes': round(total_duration / 60, 1),
                'dominant_emotion': dominant_emotion,
                'last_activity': last_activity.isoformat() if last_activity else None
            })
        
        # Sort student data
        if sort_by == 'score':
            student_data.sort(key=lambda x: x['avg_quiz_score'], reverse=True)
        elif sort_by == 'activity':
            student_data.sort(key=lambda x: x['total_activities'], reverse=True)
        else:  # recent
            student_data.sort(key=lambda x: x['last_activity'] or '', reverse=True)
        
        # Apply limit
        student_data = student_data[:limit]
        
        return jsonify({
            'status': 'success',
            'data': {
                'students': student_data,
                'total_students': len(users)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get student analytics: {str(e)}'
        }), 500


@api_bp.route('/dashboard/topics', methods=['GET'])
@role_required('teacher')
def get_topic_analytics():
    """
    Get analytics per topic (TEACHER ONLY)
    GET /api/dashboard/topics
    """
    try:
        topics = ['kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma']
        topic_data = []
        
        for topik in topics:
            # Materials count
            materials_count = TeacherMaterial.query.filter_by(topik=topik).count()
            
            # Quiz attempts for this topic
            quiz_attempts = QuizAttempt.query.filter_by(topik=topik).all()
            total_attempts = len(quiz_attempts)
            avg_score = sum(q.skor for q in quiz_attempts) / total_attempts if total_attempts > 0 else 0
            
            # Learning activities for this topic
            activities = LearningLog.query.filter(LearningLog.materi.like(f'%{topik}%')).all()
            total_activities = len(activities)
            
            # Completion rate (users who scored > 60)
            passed = sum(1 for q in quiz_attempts if q.skor >= 60)
            completion_rate = (passed / total_attempts * 100) if total_attempts > 0 else 0
            
            topic_data.append({
                'topik': topik,
                'materials_count': materials_count,
                'total_attempts': total_attempts,
                'avg_score': round(avg_score, 2),
                'total_activities': total_activities,
                'completion_rate': round(completion_rate, 2),
                'students_passed': passed
            })
        
        # Sort by popularity (most attempts)
        topic_data.sort(key=lambda x: x['total_attempts'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'topics': topic_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get topic analytics: {str(e)}'
        }), 500


@api_bp.route('/dashboard/emotions', methods=['GET'])
@role_required('teacher')
def get_emotion_analytics():
    """
    Get emotion distribution and trends (TEACHER ONLY)
    GET /api/dashboard/emotions
    Query params: ?days=7
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        # Get emotions from last N days
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        emotions = Emotion.query.filter(Emotion.waktu >= start_date).all()
        
        # Overall distribution
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion.emosi] = emotion_counts.get(emotion.emosi, 0) + 1
        
        total_emotions = len(emotions)
        emotion_distribution = {
            emosi: {
                'count': count,
                'percentage': round((count / total_emotions * 100), 2) if total_emotions > 0 else 0
            }
            for emosi, count in emotion_counts.items()
        }
        
        # Emotions by context (topic)
        context_emotions = {}
        for emotion in emotions:
            if emotion.context:
                if emotion.context not in context_emotions:
                    context_emotions[emotion.context] = {}
                context_emotions[emotion.context][emotion.emosi] = \
                    context_emotions[emotion.context].get(emotion.emosi, 0) + 1
        
        # Daily trend (last N days)
        daily_emotions = {}
        for emotion in emotions:
            date_key = emotion.waktu.date().isoformat()
            if date_key not in daily_emotions:
                daily_emotions[date_key] = {}
            daily_emotions[date_key][emotion.emosi] = \
                daily_emotions[date_key].get(emotion.emosi, 0) + 1
        
        # Sort daily emotions by date
        sorted_daily = sorted(daily_emotions.items())
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_emotions': total_emotions,
                'period_days': days,
                'distribution': emotion_distribution,
                'by_context': context_emotions,
                'daily_trend': dict(sorted_daily)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get emotion analytics: {str(e)}'
        }), 500


@api_bp.route('/dashboard/performance', methods=['GET'])
@role_required('teacher')
def get_performance_trends():
    """
    Get performance trends over time (TEACHER ONLY)
    GET /api/dashboard/performance
    Query params: ?days=30&user_id=1
    """
    try:
        days = request.args.get('days', 30, type=int)
        user_id = request.args.get('user_id', type=int)
        
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        # Build query
        query = QuizAttempt.query.filter(QuizAttempt.completed_at >= start_date)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        attempts = query.order_by(QuizAttempt.completed_at).all()
        
        # Group by date
        daily_performance = {}
        for attempt in attempts:
            date_key = attempt.completed_at.date().isoformat()
            if date_key not in daily_performance:
                daily_performance[date_key] = {
                    'total_attempts': 0,
                    'total_score': 0,
                    'scores': []
                }
            daily_performance[date_key]['total_attempts'] += 1
            daily_performance[date_key]['total_score'] += attempt.skor
            daily_performance[date_key]['scores'].append(attempt.skor)
        
        # Calculate averages
        performance_trend = []
        for date, data in sorted(daily_performance.items()):
            avg_score = data['total_score'] / data['total_attempts']
            performance_trend.append({
                'date': date,
                'avg_score': round(avg_score, 2),
                'attempts': data['total_attempts'],
                'min_score': round(min(data['scores']), 2),
                'max_score': round(max(data['scores']), 2)
            })
        
        # Overall stats
        all_scores = [a.skor for a in attempts]
        overall_stats = {
            'total_attempts': len(attempts),
            'avg_score': round(sum(all_scores) / len(all_scores), 2) if all_scores else 0,
            'min_score': round(min(all_scores), 2) if all_scores else 0,
            'max_score': round(max(all_scores), 2) if all_scores else 0
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'period_days': days,
                'user_id': user_id,
                'overall': overall_stats,
                'daily_trend': performance_trend
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get performance trends: {str(e)}'
        }), 500


# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'error': str(error)
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error': str(error)
    }), 500
