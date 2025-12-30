"""
RAG (Retrieval-Augmented Generation) Service
CRITICAL: Memastikan LLM HANYA menggunakan materi dari guru

Prinsip:
1. Materi HANYA dari teacher_materials table
2. Chunking untuk memecah materi panjang
3. Embedding sederhana (TF-IDF based)
4. Retrieve context yang relevan berdasarkan query
"""
from typing import List, Dict, Any
from app.models import TeacherMaterial, db
import re
from collections import Counter
import math


class RAGService:
    """
    Simple RAG implementation menggunakan TF-IDF
    Tanpa dependency eksternal yang berat
    """
    
    def __init__(self):
        self.chunk_size = 500  # characters per chunk
        self.chunk_overlap = 100  # overlap untuk context continuity
        self.top_k = 3  # Berapa chunk yang di-retrieve
        
        # Cache untuk materials
        self.materials_cache = []
        self.chunks_cache = []
        # Don't load materials here - will be loaded on first use
    
    def reload_materials(self):
        """
        Reload materials dari database dan rebuild chunks
        Panggil ini setiap kali ada update materi
        """
        print("🔄 Reloading teacher materials...")
        
        # Get all materials from database
        self.materials_cache = TeacherMaterial.query.all()
        
        # Build chunks
        self.chunks_cache = []
        for material in self.materials_cache:
            chunks = self._chunk_text(
                text=material.konten,
                metadata={
                    'material_id': material.id,
                    'judul': material.judul,
                    'topik': material.topik,
                    'level': material.level,
                    'created_by': material.created_by
                }
            )
            self.chunks_cache.extend(chunks)
        
        print(f"✅ Loaded {len(self.materials_cache)} materials, {len(self.chunks_cache)} chunks")
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Memecah text panjang menjadi chunks kecil
        """
        chunks = []
        
        # Clean text
        text = text.strip()
        
        # Split by paragraphs first (better semantic boundaries)
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk_size
            if len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'metadata': metadata.copy()
                    })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'text': current_chunk,
                'metadata': metadata.copy()
            })
        
        return chunks
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization: lowercase + split by non-alphanumeric
        """
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _calculate_tfidf(self, query_tokens: List[str], chunk_tokens: List[str]) -> float:
        """
        Calculate TF-IDF score untuk ranking chunks
        Simple implementation tanpa sklearn
        """
        # TF: Term frequency in chunk
        chunk_counter = Counter(chunk_tokens)
        total_chunk_tokens = len(chunk_tokens)
        
        # Calculate score
        score = 0.0
        for token in query_tokens:
            if token in chunk_counter:
                tf = chunk_counter[token] / total_chunk_tokens
                # Simple scoring: just TF for now (no IDF karena corpus kecil)
                score += tf
        
        return score
    
    def retrieve_context(self, query: str, topik: str = None, level: str = None, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context dari teacher materials
        
        Args:
            query: User's question atau topic
            topik: Filter by topik (optional)
            level: Filter by level (optional)
            top_k: Number of chunks to retrieve (default: self.top_k)
        
        Returns:
            List of relevant chunks dengan metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        # Reload materials if cache is empty
        if not self.chunks_cache:
            self.reload_materials()
        
        if not self.chunks_cache:
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        # Filter chunks by topik/level if specified
        filtered_chunks = self.chunks_cache
        if topik:
            filtered_chunks = [c for c in filtered_chunks if c['metadata']['topik'] == topik.lower()]
        if level:
            filtered_chunks = [c for c in filtered_chunks if c['metadata']['level'] == level.lower()]
        
        if not filtered_chunks:
            # No matching chunks, return all
            filtered_chunks = self.chunks_cache
        
        # Score each chunk
        scored_chunks = []
        for chunk in filtered_chunks:
            chunk_tokens = self._tokenize(chunk['text'])
            score = self._calculate_tfidf(query_tokens, chunk_tokens)
            
            # Boost score if query token in title
            title_tokens = self._tokenize(chunk['metadata']['judul'])
            for token in query_tokens:
                if token in title_tokens:
                    score += 0.5  # Title match bonus
            
            scored_chunks.append({
                'chunk': chunk,
                'score': score
            })
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top_k chunks
        top_chunks = scored_chunks[:top_k]
        
        # Format result
        results = []
        for item in top_chunks:
            results.append({
                'text': item['chunk']['text'],
                'score': item['score'],
                'metadata': item['chunk']['metadata']
            })
        
        return results
    
    def get_material_by_topik(self, topik: str, level: str = None) -> str:
        """
        Get full material by topik
        Untuk kasus dimana kita butuh semua materi tentang topik tertentu
        """
        query = TeacherMaterial.query.filter_by(topik=topik.lower())
        
        if level:
            query = query.filter_by(level=level.lower())
        
        materials = query.all()
        
        if not materials:
            return ""
        
        # Combine all materials for this topik
        combined_text = ""
        for mat in materials:
            combined_text += f"\n\n=== {mat.judul} (oleh {mat.created_by}) ===\n\n"
            combined_text += mat.konten
        
        return combined_text.strip()
    
    def format_context_for_llm(self, contexts: List[Dict[str, Any]]) -> str:
        """
        Format retrieved contexts untuk LLM prompt
        """
        if not contexts:
            return "Tidak ada materi yang tersedia."
        
        formatted = "=== MATERI DARI GURU ===\n\n"
        
        for i, ctx in enumerate(contexts, 1):
            formatted += f"[Materi {i}] {ctx['metadata']['judul']}\n"
            formatted += f"Topik: {ctx['metadata']['topik']} | Level: {ctx['metadata']['level']}\n"
            formatted += f"Oleh: {ctx['metadata']['created_by']}\n\n"
            formatted += ctx['text']
            formatted += "\n\n" + "="*50 + "\n\n"
        
        return formatted


# Global instance
rag_service = RAGService()
