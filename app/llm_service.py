"""
LLM Service using Google Gemini
Untuk generate penjelasan adaptif yang natural

CRITICAL UPDATE: Sekarang menggunakan RAG (Retrieval-Augmented Generation)
- LLM HANYA menggunakan materi dari guru
- Context di-retrieve dari teacher_materials via RAG service
"""
import os
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.rag_service import rag_service

class LLMService:
    """
    Service untuk interact dengan Google Gemini LLM
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        use_llm_env = os.getenv('USE_LLM', 'False')
        self.use_llm = use_llm_env.lower() == 'true'
        self.model = None
        
        # Debug logging
        print(f"🔍 LLM Service Initialization:")
        print(f"   USE_LLM env: '{use_llm_env}'")
        print(f"   use_llm (parsed): {self.use_llm}")
        print(f"   API_KEY present: {bool(self.api_key)}")
        if self.api_key:
            print(f"   API_KEY length: {len(self.api_key)} chars")
        
        if self.use_llm and self.api_key and self.api_key != 'your_gemini_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                # Using Gemini 1.5 Flash - faster and more efficient
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ LLM (Google Gemini Flash 2.5) initialized successfully")
            except Exception as e:
                print(f"⚠️ LLM initialization failed: {e}")
                self.use_llm = False
        else:
            print(f"ℹ️  LLM disabled - using rule-based content")
            if not self.use_llm:
                print(f"   Reason: USE_LLM={use_llm_env} (expected 'True')")
            elif not self.api_key:
                print(f"   Reason: No API key found")
            elif self.api_key == 'your_gemini_api_key_here':
                print(f"   Reason: API key not set (placeholder)")

    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        return self.use_llm and self.model is not None
    
    def generate_explanation(self,
                           topic: str,
                           learning_style: str,
                           difficulty: str,
                           emotion: str,
                           user_query: str = None) -> Optional[str]:
        """
        Generate adaptive explanation using LLM + RAG
        
        Args:
            topic: Topik matematika (kubus, balok, dll)
            learning_style: visual, auditori, kinestetik
            difficulty: pemula, menengah, mahir
            emotion: cemas, bingung, netral, percaya_diri
            user_query: Specific question dari user (optional)
            
        Returns:
            Generated explanation or None if LLM unavailable
        """
        print(f"🔍 LLM generate_explanation called:")
        print(f"   - is_available: {self.is_available()}")
        print(f"   - model: {self.model}")
        
        if not self.is_available():
            print("   ❌ LLM not available, returning None")
            return None
        
        # CRITICAL: Retrieve context dari guru materials via RAG
        query = user_query if user_query else topic
        contexts = rag_service.retrieve_context(
            query=query,
            topik=topic,
            level=difficulty,
            top_k=3
        )
        
        if not contexts:
            print("   ⚠️ No teacher materials found! Using fallback.")
            return None
        
        print(f"   ✅ Retrieved {len(contexts)} context chunks from teacher materials")
        
        # Build prompt with RAG context
        prompt = self._build_rag_prompt(
            contexts=contexts,
            topic=topic,
            learning_style=learning_style,
            difficulty=difficulty,
            emotion=emotion,
            user_query=user_query
        )
        
        print("   ✅ LLM is available, generating content...")
        
        try:
            response = self.model.generate_content(prompt)
            print(f"   ✅ LLM response received! Length: {len(response.text)} chars")
            return response.text
        except Exception as e:
            print(f"   ❌ LLM generation error: {e}")
            return None
    
    def _build_rag_prompt(self,
                         contexts: list,
                         topic: str,
                         learning_style: str,
                         difficulty: str,
                         emotion: str,
                         user_query: str = None) -> str:
        """
        Build prompt dengan RAG context dari materi guru
        CRITICAL: LLM HANYA boleh menggunakan informasi dari contexts
        """
        
        # Format contexts
        context_text = rag_service.format_context_for_llm(contexts)
        
        # Learning style instructions
        style_instructions = {
            'visual': "Gunakan banyak analogi visual dan perbandingan gambar. Jelaskan dengan cara yang mudah divisualisasikan.",
            'auditori': "Gunakan penjelasan verbal yang jelas dan terstruktur. Jelaskan step-by-step seperti sedang berbicara.",
            'kinestetik': "Fokus pada aktivitas praktik dan contoh kehidupan sehari-hari yang bisa dipraktikkan."
        }
        
        # Emotion-based tone
        emotion_tones = {
            'cemas': "Gunakan nada yang menenangkan dan supportive. Mulai dari konsep paling dasar. Berikan encouragement.",
            'bingung': "Gunakan nada yang patient. Breakdown konsep menjadi bagian kecil. Berikan banyak contoh.",
            'netral': "Gunakan nada yang informatif dan balanced.",
            'percaya_diri': "Gunakan nada yang challenging. Boleh masuk ke detail lebih dalam."
        }
        
        # Difficulty level
        difficulty_guides = {
            'pemula': "Jelaskan dengan sangat sederhana, seperti menjelaskan ke anak SMP.",
            'menengah': "Jelaskan dengan detail tapi tetap accessible, setara siswa SMA.",
            'mahir': "Boleh menggunakan terminologi advanced dan konsep matematika yang lebih kompleks."
        }
        
        query_instruction = f"\n\nPERTANYAAN SPESIFIK: {user_query}" if user_query else ""
        
        prompt = f"""
Kamu adalah AI tutor matematika EMOTIVA-MATH.

🚨 ATURAN MUTLAK (CRITICAL):
1. Kamu HANYA BOLEH menggunakan informasi dari MATERI DARI GURU di bawah
2. DILARANG menggunakan pengetahuan eksternal atau membuat informasi sendiri
3. Jika informasi tidak ada di materi guru, katakan dengan jujur
4. Kamu bertugas MENYAMPAIKAN ULANG materi guru secara adaptif

{context_text}

KONTEKS SISWA:
- Gaya Belajar: {learning_style.upper()}
- Level: {difficulty.upper()}
- Kondisi Emosi: {emotion.upper()}

INSTRUKSI PENYAMPAIAN:
- {style_instructions.get(learning_style, '')}
- {emotion_tones.get(emotion, '')}
- {difficulty_guides.get(difficulty, '')}
{query_instruction}

TUGAS:
Sampaikan materi tentang {topic} kepada siswa dengan cara yang:
1. Sesuai dengan gaya belajar mereka ({learning_style})
2. Sesuai dengan level mereka ({difficulty})
3. Sesuai dengan kondisi emosi mereka ({emotion})

FORMAT OUTPUT:
1. **Salam Pembuka** - Greeting yang sesuai emosi
2. **Penjelasan Materi** - Sampaikan materi guru dengan cara adaptif
3. **Contoh/Ilustrasi** - Jika ada contoh di materi guru, jelaskan dengan baik
4. **Motivasi Penutup** - Tutup dengan motivasi sesuai emosi

PENTING:
- Gunakan bahasa Indonesia yang natural dan friendly
- Gunakan emoji yang relevan untuk visual aids
- JANGAN tambahkan informasi di luar materi guru
- Jika materi guru belum lengkap, akui dengan jujur

Mulai penjelasan sekarang:
"""
        return prompt.strip()
    
    def _build_prompt(self,
                     topic: str,
                     learning_style: str, 
                     difficulty: str,
                     emotion: str) -> str:
        """Build detailed prompt for Gemini"""
        
        # Learning style instructions
        style_instructions = {
            'visual': """
Gunakan banyak analogi visual, diagram deskriptif, dan perbandingan gambar.
Jelaskan dengan cara yang mudah divisualisasikan dalam pikiran.
Gunakan emoji dan karakter visual untuk memperjelas.
            """,
            'auditori': """
Gunakan penjelasan verbal yang jelas dan terstruktur.
Jelaskan step-by-step seperti sedang berbicara langsung.
Gunakan analogi yang mudah didengar dan diingat.
            """,
            'kinestetik': """
Fokus pada aktivitas praktik dan hands-on learning.
Berikan instruksi konkret yang bisa langsung dipraktikkan.
Gunakan contoh dari kehidupan sehari-hari yang bisa disentuh/dilihat.
            """
        }
        
        # Emotion-based tone
        emotion_tones = {
            'cemas': """
Gunakan nada yang menenangkan dan supportive.
Mulai dari konsep paling dasar.
Berikan banyak encouragement dan positive reinforcement.
Hindari istilah yang terlalu teknis.
            """,
            'bingung': """
Gunakan nada yang patient dan explanatory.
Breakdown konsep menjadi bagian-bagian kecil.
Berikan banyak contoh dan analogi.
Ulangi poin-poin penting dengan cara berbeda.
            """,
            'netral': """
Gunakan nada yang informatif dan balanced.
Berikan penjelasan yang comprehensive tapi tidak overwhelming.
            """,
            'percaya_diri': """
Gunakan nada yang challenging dan engaging.
Boleh masuk ke detail yang lebih dalam.
Tambahkan fun facts dan advanced insights.
            """
        }
        
        # Difficulty level
        difficulty_guides = {
            'pemula': "Jelaskan dengan sangat sederhana, seperti menjelaskan ke anak SMP.",
            'menengah': "Jelaskan dengan detail tapi tetap accessible, setara siswa SMA.",
            'mahir': "Boleh menggunakan terminologi advanced dan konsep matematika yang lebih kompleks."
        }
        
        # Topic info
        topic_info = {
            'kubus': 'Kubus adalah bangun ruang dengan 6 sisi berbentuk persegi yang sama besar',
            'balok': 'Balok adalah bangun ruang dengan 6 sisi berbentuk persegi panjang',
            'bola': 'Bola adalah bangun ruang berbentuk bulat sempurna',
            'tabung': 'Tabung adalah bangun ruang dengan alas dan tutup berbentuk lingkaran',
            'kerucut': 'Kerucut adalah bangun ruang dengan alas lingkaran dan puncak',
        }
        
        prompt = f"""
Kamu adalah AI tutor matematika yang expert dalam adaptive learning.

TUGAS: Buatkan penjelasan tentang "{topic.upper()}" dalam bahasa Indonesia yang natural dan engaging.

KONTEKS SISWA:
- Gaya Belajar: {learning_style.upper()}
- Level: {difficulty.upper()}
- Kondisi Emosi: {emotion.upper()}

INSTRUKSI GAYA BELAJAR:
{style_instructions.get(learning_style, '')}

INSTRUKSI TONE BERDASARKAN EMOSI:
{emotion_tones.get(emotion, '')}

INSTRUKSI DIFFICULTY:
{difficulty_guides.get(difficulty, '')}

TOPIK: {topic_info.get(topic, topic)}

FORMAT OUTPUT:
1. **Pengenalan** - Buka dengan greeting yang sesuai emosi siswa
2. **Definisi** - Jelaskan apa itu {topic} dengan cara yang sesuai gaya belajar
3. **Komponen/Bagian** - Jelaskan sisi, rusuk, titik sudut (jika ada)
4. **Rumus** - Jelaskan rumus volume dan luas permukaan dengan clear
5. **Contoh Sederhana** - Berikan 1 contoh perhitungan yang mudah
6. **Tips Belajar** - Berikan 2-3 tips spesifik untuk gaya belajar {learning_style}
7. **Motivasi Penutup** - Tutup dengan motivasi yang sesuai dengan emosi {emotion}

PENTING:
- Gunakan bahasa Indonesia yang natural dan friendly
- Hindari jargon yang terlalu formal
- Gunakan emoji yang relevan untuk visual aids
- Pastikan penjelasan sesuai dengan gaya belajar {learning_style}
- Sesuaikan kompleksitas dengan level {difficulty}
- Tone harus cocok dengan emosi {emotion}

Mulai penjelasan sekarang:
"""
        return prompt.strip()
    
    def generate_motivation(self, emotion: str, context: str = "") -> Optional[str]:
        """Generate personalized motivation message"""
        if not self.is_available():
            return None
        
        prompt = f"""
Buatkan 1 kalimat motivasi yang warm dan encouraging dalam bahasa Indonesia untuk siswa yang sedang {emotion}.
Context: {context if context else "sedang belajar matematika"}

Gunakan emoji yang cocok. Jangan terlalu panjang (maksimal 2 kalimat).
Harus terasa personal dan genuine.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return None
    
    def generate_practice_question(self,
                                   topic: str,
                                   difficulty: str) -> Optional[Dict[str, str]]:
        """Generate practice question using LLM"""
        if not self.is_available():
            return None
        
        prompt = f"""
Buatkan 1 soal latihan tentang {topic} dengan tingkat kesulitan {difficulty}.

Format output (gunakan format ini PERSIS):
SOAL: [tulis soal di sini]
PEMBAHASAN: [tulis step-by-step solution]
JAWABAN: [tulis jawaban final]

Pastikan:
- Soal dalam bahasa Indonesia
- Angka-angka yang digunakan mudah dihitung
- Pembahasan step-by-step yang jelas
- Difficulty sesuai level {difficulty}
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse response
            parts = text.split('PEMBAHASAN:')
            if len(parts) == 2:
                question = parts[0].replace('SOAL:', '').strip()
                temp = parts[1].split('JAWABAN:')
                if len(temp) == 2:
                    solution = temp[0].strip()
                    answer = temp[1].strip()
                    return {
                        'question': question,
                        'solution': solution,
                        'answer': answer
                    }
            
            return None
        except:
            return None
    
    def generate_visualization_json(self,
                                   topic: str,
                                   difficulty: str = 'pemula',
                                   context: str = None) -> Optional[Dict[str, Any]]:
        """
        Generate DECLARATIVE JSON for 3D visualization
        CRITICAL: LLM HANYA generate JSON, BUKAN code JavaScript
        
        Args:
            topic: Topik bangun ruang (kubus, balok, bola, dll)
            difficulty: Level kesulitan
            context: Konteks tambahan (misal: "jelaskan volume")
            
        Returns:
            JSON object yang AMAN untuk di-render
        """
        if not self.is_available():
            return None
        
        prompt = f"""
TUGAS: Generate JSON untuk visualisasi 3D bangun ruang "{topic.upper()}"

⚠️ ATURAN MUTLAK:
1. Output HANYA JSON, TIDAK BOLEH ada code JavaScript
2. Format JSON harus PERSIS seperti spesifikasi
3. Tidak boleh ada function, eval(), atau executable code

SPESIFIKASI JSON:
{{
  "type": "visualization",
  "title": "Nama Bangun Ruang",
  "description": "Penjelasan singkat",
  "objects": [
    {{
      "id": "obj1",
      "type": "box|sphere|cylinder|cone",
      "color": "#RRGGBB",
      "position": [x, y, z],
      "scale": [width, height, depth],
      "rotation": [x, y, z],
      "wireframe": false,
      "label": "Label untuk object",
      "opacity": 1.0
    }}
  ],
  "camera": {{
    "position": [x, y, z],
    "lookAt": [x, y, z]
  }},
  "annotations": [
    {{
      "text": "Teks annotation",
      "position": [x, y, z],
      "color": "#RRGGBB"
    }}
  ],
  "animation": {{
    "rotate": true,
    "speed": 1
  }}
}}

PANDUAN PER TOPIK:
- KUBUS: box dengan scale [2,2,2], warna solid
- BALOK: box dengan scale berbeda [3,2,1.5]
- BOLA: sphere dengan radius 1.5
- TABUNG: cylinder dengan radiusTop=radiusBottom
- KERUCUT: cone dengan radiusBottom dan apex

Context: {context if context else "Visualisasi dasar"}
Difficulty: {difficulty}

OUTPUT (HANYA JSON VALID):
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean markdown code blocks if present
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1])
            
            # Parse JSON
            import json
            viz_json = json.loads(text)
            
            # Validate structure
            if 'objects' not in viz_json or not isinstance(viz_json['objects'], list):
                print("⚠️ Invalid visualization JSON structure")
                return None
            
            print(f"✅ Generated visualization JSON with {len(viz_json['objects'])} objects")
            return viz_json
            
        except json.JSONDecodeError as e:
            print(f"❌ LLM returned invalid JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Visualization generation error: {e}")
            return None
    
    def generate_quiz_questions(
        self, 
        topik: str, 
        level: str = 'pemula',
        num_questions: int = 5
    ) -> Optional[list]:
        """
        Generate quiz questions using RAG context from teacher materials
        
        Args:
            topik: Topic (kubus, balok, bola, etc.)
            level: Difficulty level
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with keys:
            - pertanyaan: Question text
            - pilihan_a, pilihan_b, pilihan_c, pilihan_d: Answer choices
            - jawaban_benar: Correct answer (A, B, C, or D)
            - penjelasan: Explanation of the correct answer
        """
        if not self.use_llm:
            print("ℹ️ LLM disabled, cannot generate quiz")
            return None
        
        # Retrieve context from RAG
        contexts = rag_service.retrieve_context(
            query=topik,
            topik=topik,
            level=level,
            top_k=3
        )
        
        if not contexts:
            print(f"⚠️ No teacher materials found for {topik}/{level}")
            return None
        
        # Format contexts untuk prompt
        formatted_context = "\n\n---\n\n".join([
            f"MATERI: {ctx['metadata']['judul']}\n{ctx['text']}"
            for ctx in contexts
        ])
        
        print(f"✅ Retrieved {len(contexts)} context chunks for quiz generation")
        
        prompt = f"""Kamu adalah guru matematika yang membuat soal latihan.

KONTEKS MATERI DARI GURU:
{formatted_context}

Buatlah {num_questions} soal pilihan ganda berkualitas tinggi untuk topik "{topik}" level "{level}".

ATURAN PENTING:
1. Soal HARUS berdasarkan materi guru di atas
2. JANGAN membuat informasi baru di luar materi guru
3. Setiap soal harus punya 4 pilihan jawaban (A, B, C, D)
4. Hanya 1 jawaban yang benar
5. Berikan penjelasan singkat untuk jawaban benar
6. Variasi tingkat kesulitan dalam level yang sama
7. Hindari soal yang terlalu mudah ditebak

FORMAT OUTPUT (JSON ARRAY):
[
  {{
    "pertanyaan": "Teks soal lengkap dengan angka jika ada",
    "pilihan_a": "Pilihan A",
    "pilihan_b": "Pilihan B",
    "pilihan_c": "Pilihan C",
    "pilihan_d": "Pilihan D",
    "jawaban_benar": "A",
    "penjelasan": "Penjelasan singkat mengapa A benar"
  }}
]

OUTPUT (HANYA JSON ARRAY):
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean markdown code blocks if present
            if text.startswith('```'):
                lines = text.split('\n')
                # Remove first and last line (``` markers)
                text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text
                # Remove json language identifier
                text = text.replace('json', '', 1).strip()
            
            # Parse JSON
            import json
            questions = json.loads(text)
            
            # Validate structure
            if not isinstance(questions, list):
                print("⚠️ Invalid quiz JSON structure - not a list")
                return None
            
            # Validate each question
            required_keys = ['pertanyaan', 'pilihan_a', 'pilihan_b', 'pilihan_c', 
                           'pilihan_d', 'jawaban_benar', 'penjelasan']
            valid_questions = []
            
            for q in questions:
                if all(key in q for key in required_keys):
                    # Validate jawaban_benar is A, B, C, or D
                    if q['jawaban_benar'].upper() in ['A', 'B', 'C', 'D']:
                        q['jawaban_benar'] = q['jawaban_benar'].upper()
                        valid_questions.append(q)
                    else:
                        print(f"⚠️ Invalid answer key: {q['jawaban_benar']}")
                else:
                    print(f"⚠️ Question missing required keys")
            
            if not valid_questions:
                print("❌ No valid questions generated")
                return None
            
            print(f"✅ Generated {len(valid_questions)} valid quiz questions")
            return valid_questions
            
        except json.JSONDecodeError as e:
            print(f"❌ LLM returned invalid JSON: {e}")
            print(f"Response text: {text[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Quiz generation error: {e}")
            return None


# Singleton instance
llm_service = LLMService()
