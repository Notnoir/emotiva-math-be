from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import db, User, Emotion, LearningLog, TeacherMaterial
from app.ai_engine import adaptive_engine
from app.llm_service import llm_service

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
            'visualization': '/api/visualization/generate [POST]'
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
def get_adaptive_content():
    """
    POST /api/adaptive/content - Get adaptive learning content
    
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
def handle_materials():
    """
    GET /api/materials - Get all materials atau filter berdasarkan topik/level
    POST /api/materials - Upload materi baru (GURU ONLY)
    
    Query params untuk GET:
        - topik: string (opsional)
        - level: string (opsional)
    
    Body untuk POST:
        {
            "judul": string,
            "topik": string (kubus, balok, bola, tabung, kerucut, limas, prisma),
            "konten": string (materi lengkap),
            "level": string (pemula, menengah, mahir),
            "created_by": string (nama guru)
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
        
        # Create material
        material = TeacherMaterial(
            judul=data['judul'],
            topik=data['topik'].lower(),
            konten=data['konten'],
            level=level,
            created_by=data.get('created_by', 'Admin')
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Material uploaded successfully',
            'data': material.to_dict()
        }), 201

@api_bp.route('/materials/<int:material_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_material_detail(material_id):
    """
    GET /api/materials/<id> - Get specific material
    PUT /api/materials/<id> - Update material (GURU ONLY)
    DELETE /api/materials/<id> - Delete material (GURU ONLY)
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
        if 'created_by' in data:
            material.created_by = data['created_by']
        
        material.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Material updated successfully',
            'data': material.to_dict()
        }), 200
    
    elif request.method == 'DELETE':
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

# ==================== ERROR HANDLERS ====================

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
