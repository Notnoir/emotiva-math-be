"""
Adaptive Learning Engine - AI Core
Hybrid: Rule-based AI + LLM untuk personalisasi pembelajaran
"""
from typing import Dict, List, Any
import random
from app.llm_service import llm_service


class AdaptiveLearningEngine:
    """
    AI Engine untuk adaptive learning
    Menggabungkan: learning style, emotion, level, dan performance
    """
    
    def __init__(self):
        self.topics = {
            'kubus': {
                'name': 'Kubus',
                'difficulty': 'pemula',
                'concepts': ['definisi', 'sisi', 'rusuk', 'titik_sudut', 'volume', 'luas_permukaan']
            },
            'balok': {
                'name': 'Balok',
                'difficulty': 'pemula',
                'concepts': ['definisi', 'perbedaan_kubus', 'volume', 'luas_permukaan']
            },
            'bola': {
                'name': 'Bola',
                'difficulty': 'menengah',
                'concepts': ['definisi', 'jari-jari', 'diameter', 'volume', 'luas_permukaan']
            },
            'tabung': {
                'name': 'Tabung',
                'difficulty': 'menengah',
                'concepts': ['definisi', 'alas', 'tinggi', 'volume', 'luas_permukaan']
            },
            'kerucut': {
                'name': 'Kerucut',
                'difficulty': 'menengah',
                'concepts': ['definisi', 'alas', 'tinggi', 'garis_pelukis', 'volume', 'luas_permukaan']
            },
            'limas': {
                'name': 'Limas',
                'difficulty': 'mahir',
                'concepts': ['definisi', 'jenis', 'alas', 'tinggi', 'volume', 'luas_permukaan']
            }
        }
    
    def generate_content(self, 
                        topic: str,
                        learning_style: str,
                        emotion: str,
                        level: str,
                        previous_scores: List[int] = None) -> Dict[str, Any]:
        """
        Generate adaptive content berdasarkan profile user
        
        Args:
            topic: Topik yang dipelajari (kubus, balok, dll)
            learning_style: visual, auditori, kinestetik
            emotion: cemas, bingung, netral, percaya_diri
            level: pemula, menengah, mahir
            previous_scores: List skor latihan sebelumnya
            
        Returns:
            Dictionary berisi konten adaptif
        """
        
        # Calculate difficulty adjustment
        adjusted_difficulty = self._adjust_difficulty(level, emotion, previous_scores)
        
        # Generate explanation based on learning style (LLM-powered if available)
        explanation = self._generate_explanation(topic, learning_style, adjusted_difficulty, emotion)
        
        # Generate exercises
        exercises = self._generate_exercises(topic, adjusted_difficulty)
        
        # Generate motivation message based on emotion
        motivation = self._generate_motivation(emotion)
        
        # Recommend next topic
        next_topic = self._recommend_next_topic(topic, level, previous_scores)
        
        return {
            'topic': topic,
            'topic_name': self.topics.get(topic, {}).get('name', topic),
            'difficulty': adjusted_difficulty,
            'learning_style': learning_style,
            'content': {
                'explanation': explanation,
                'visual_aids': self._get_visual_aids(topic, learning_style),
                'examples': self._generate_examples(topic, adjusted_difficulty),
                'key_formulas': self._get_formulas(topic)
            },
            'exercises': exercises,
            'motivation': motivation,
            'recommendations': {
                'next_topic': next_topic,
                'learning_tips': self._get_learning_tips(learning_style, emotion),
                'estimated_time': self._estimate_time(adjusted_difficulty)
            }
        }
    
    def _adjust_difficulty(self, level: str, emotion: str, previous_scores: List[int]) -> str:
        """Adjust difficulty berdasarkan level, emotion, dan performance"""
        
        # Base difficulty dari level
        difficulty_map = {'pemula': 1, 'menengah': 2, 'mahir': 3}
        base_difficulty = difficulty_map.get(level, 1)
        
        # Adjust based on emotion
        emotion_adjustment = {
            'cemas': -1,          # Turunkan difficulty
            'bingung': -0.5,      # Turunkan sedikit
            'netral': 0,          # Tidak berubah
            'percaya_diri': 0.5   # Naikkan sedikit
        }
        
        difficulty = base_difficulty + emotion_adjustment.get(emotion, 0)
        
        # Adjust based on previous scores
        if previous_scores and len(previous_scores) >= 3:
            avg_score = sum(previous_scores[-3:]) / 3
            if avg_score >= 80:
                difficulty += 0.5  # Increase if performing well
            elif avg_score < 60:
                difficulty -= 0.5  # Decrease if struggling
        
        # Map back to difficulty level
        if difficulty <= 1.5:
            return 'pemula'
        elif difficulty <= 2.5:
            return 'menengah'
        else:
            return 'mahir'
    
    def _generate_explanation(self, topic: str, learning_style: str, difficulty: str, emotion: str = 'netral', user_query: str = None) -> str:
        """Generate penjelasan berdasarkan learning style - LLM + RAG first, fallback to rule-based"""
        
        # Try LLM + RAG first
        if llm_service.is_available():
            llm_explanation = llm_service.generate_explanation(
                topic=topic,
                learning_style=learning_style,
                difficulty=difficulty,
                emotion=emotion,
                user_query=user_query  # Pass user query for RAG
            )
            if llm_explanation:
                return llm_explanation
        
        # Fallback to rule-based if LLM unavailable
        explanations = {
            'kubus': {
                'visual': """
🟦 **KUBUS - Penjelasan Visual**

Bayangkan sebuah dadu! Itulah bentuk kubus. 

📐 **Karakteristik:**
• Memiliki 6 sisi berbentuk persegi yang sama
• Semua rusuk memiliki panjang yang sama (s)
• Total 12 rusuk, 8 titik sudut

📊 **Rumus:**
• Volume = s × s × s = s³
• Luas Permukaan = 6 × s²

💡 **Visualisasi:** Lihat gambar 3D di bawah untuk memahami struktur kubus!
                """,
                'auditori': """
🎧 **KUBUS - Penjelasan Audio**

Dengarkan baik-baik penjelasan tentang kubus:

Kubus adalah bangun ruang yang memiliki enam sisi berbentuk persegi. Semua sisinya sama besar dan semua rusuknya sama panjang. 

Untuk menghitung volume kubus, kita kalikan panjang rusuk tiga kali (s pangkat tiga). Sedangkan untuk luas permukaan, kita kalikan 6 dengan luas satu sisi persegi (6 dikali s kuadrat).

Ingat: "Kubus = Dadu = Semua sisi sama!"
                """,
                'kinestetik': """
✋ **KUBUS - Praktik Langsung**

Mari kita praktik memahami kubus!

🎯 **Aktivitas:**
1. Ambil kardus bekas atau kertas
2. Buat 6 persegi dengan ukuran sama (misal 5cm × 5cm)
3. Satukan menjadi kubus

🧮 **Latihan Hitung:**
Jika rusuk kubus = 5 cm, maka:
• Volume = 5 × 5 × 5 = 125 cm³
• Luas Permukaan = 6 × (5 × 5) = 150 cm²

💪 Coba buat kubus dengan ukuran berbeda dan hitung sendiri!
                """
            }
        }
        
        # Get explanation for topic and style
        topic_explanations = explanations.get(topic, {})
        explanation = topic_explanations.get(learning_style, topic_explanations.get('visual', 'Materi sedang dikembangkan...'))
        
        return explanation.strip()
    
    def _get_visual_aids(self, topic: str, learning_style: str) -> List[str]:
        """Get visual aids recommendations"""
        
        visual_aids = {
            'kubus': [
                '3D model interaktif kubus',
                'Diagram rusuk dan sisi',
                'Animasi rotasi kubus',
                'Perbandingan kubus berbagai ukuran'
            ],
            'balok': [
                '3D model interaktif balok',
                'Perbedaan kubus vs balok',
                'Diagram dimensi (p, l, t)',
                'Contoh balok dalam kehidupan'
            ]
        }
        
        aids = visual_aids.get(topic, ['Diagram dasar', 'Contoh gambar'])
        
        # Emphasize visual aids for visual learners
        if learning_style == 'visual':
            aids.append('Video penjelasan animasi')
        
        return aids
    
    def _generate_examples(self, topic: str, difficulty: str) -> List[Dict[str, str]]:
        """Generate contoh soal berdasarkan difficulty"""
        
        examples_db = {
            'kubus': {
                'pemula': [
                    {
                        'question': 'Sebuah kubus memiliki panjang rusuk 4 cm. Berapa volume kubus tersebut?',
                        'solution': 'Volume = s³ = 4³ = 4 × 4 × 4 = 64 cm³',
                        'answer': '64 cm³'
                    },
                    {
                        'question': 'Kubus dengan rusuk 3 cm memiliki luas permukaan berapa?',
                        'solution': 'Luas Permukaan = 6 × s² = 6 × 3² = 6 × 9 = 54 cm²',
                        'answer': '54 cm²'
                    }
                ],
                'menengah': [
                    {
                        'question': 'Jika volume kubus adalah 216 cm³, berapa panjang rusuknya?',
                        'solution': 's³ = 216, maka s = ∛216 = 6 cm',
                        'answer': '6 cm'
                    }
                ],
                'mahir': [
                    {
                        'question': 'Sebuah kubus diperbesar 2 kali. Berapa kali volume kubus yang baru dibanding yang lama?',
                        'solution': 'Volume lama = s³, Volume baru = (2s)³ = 8s³. Jadi 8 kali lipat.',
                        'answer': '8 kali lipat'
                    }
                ]
            }
        }
        
        topic_examples = examples_db.get(topic, {})
        return topic_examples.get(difficulty, topic_examples.get('pemula', []))
    
    def _get_formulas(self, topic: str) -> Dict[str, str]:
        """Get key formulas for topic"""
        
        formulas = {
            'kubus': {
                'Volume': 's³ atau s × s × s',
                'Luas Permukaan': '6 × s²',
                'Diagonal Bidang': 's√2',
                'Diagonal Ruang': 's√3'
            },
            'balok': {
                'Volume': 'p × l × t',
                'Luas Permukaan': '2(pl + pt + lt)',
                'Diagonal Bidang': '√(p² + l²) atau √(p² + t²) atau √(l² + t²)',
                'Diagonal Ruang': '√(p² + l² + t²)'
            }
        }
        
        return formulas.get(topic, {'Volume': 'Formula sedang dikembangkan'})
    
    def _generate_exercises(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate latihan soal"""
        
        # Simple exercise generation (bisa diperluas dengan soal random)
        exercises = [
            {
                'id': 1,
                'type': 'multiple_choice',
                'question': f'Soal latihan {topic} - Level {difficulty}',
                'difficulty': difficulty,
                'points': 10
            }
        ]
        
        return exercises
    
    def _generate_motivation(self, emotion: str) -> str:
        """Generate motivational message based on emotion"""
        
        messages = {
            'cemas': '💪 Tenang! Kita akan mulai dari dasar. Tidak ada yang terlalu sulit jika dipelajari step by step!',
            'bingung': '🤔 Tidak apa-apa merasa bingung! Itu tandanya otak sedang belajar. Mari kita coba pendekatan yang berbeda!',
            'netral': '📚 Bagus! Mari kita fokus dan pelajari materi ini dengan seksama.',
            'percaya_diri': '🌟 Hebat! Kepercayaan diri Anda tinggi. Mari kita coba tantangan yang lebih menarik!'
        }
        
        return messages.get(emotion, '✨ Mari kita mulai belajar!')
    
    def _recommend_next_topic(self, current_topic: str, level: str, previous_scores: List[int]) -> str:
        """Recommend next learning topic"""
        
        topic_sequence = {
            'pemula': ['kubus', 'balok', 'bola'],
            'menengah': ['tabung', 'kerucut', 'limas'],
            'mahir': ['limas', 'prisma', 'gabungan_bangun']
        }
        
        current_sequence = topic_sequence.get(level, topic_sequence['pemula'])
        
        try:
            current_index = current_sequence.index(current_topic)
            if current_index < len(current_sequence) - 1:
                return current_sequence[current_index + 1]
        except ValueError:
            pass
        
        return current_sequence[0] if current_sequence else 'kubus'
    
    def _get_learning_tips(self, learning_style: str, emotion: str) -> List[str]:
        """Get personalized learning tips"""
        
        style_tips = {
            'visual': [
                'Gambar diagram sendiri untuk lebih paham',
                'Gunakan warna berbeda untuk setiap rumus',
                'Tonton video visualisasi 3D'
            ],
            'auditori': [
                'Bacakan rumus dengan keras',
                'Diskusikan dengan teman',
                'Dengarkan penjelasan berulang kali'
            ],
            'kinestetik': [
                'Buat model 3D dari kertas/kardus',
                'Praktik menghitung dengan benda nyata',
                'Gerakkan tangan saat menjelaskan'
            ]
        }
        
        tips = style_tips.get(learning_style, style_tips['visual'])
        
        # Add emotion-specific tip
        if emotion == 'cemas':
            tips.append('⭐ Mulai dari soal termudah untuk build confidence')
        elif emotion == 'percaya_diri':
            tips.append('⭐ Challenge yourself dengan soal yang lebih kompleks')
        
        return tips[:3]  # Return top 3 tips
    
    def _estimate_time(self, difficulty: str) -> int:
        """Estimate learning time in minutes"""
        
        time_map = {
            'pemula': 15,
            'menengah': 25,
            'mahir': 35
        }
        
        return time_map.get(difficulty, 20)


# Singleton instance
adaptive_engine = AdaptiveLearningEngine()
