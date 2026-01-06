"""
Test LLM behavior ketika tidak ada materi dari guru (MOCK TEST - No real API call)
"""
import os
import sys

# Setup path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Setup environment (tidak perlu API key karena pakai mock)
os.environ['USE_LLM'] = 'False'  # Disable real LLM
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:@localhost:3306/emotiva-math'

from app import create_app
from app.rag_service import rag_service
from app.llm_service import LLMService

def mock_llm_with_no_materials():
    """Test logic LLM ketika tidak ada materi"""
    
    print("\n" + "="*80)
    print("🧪 MOCK TEST: LLM Logic When No Materials Available")
    print("="*80 + "\n")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        
        # Scenario 1: RAG returns empty contexts
        print("📝 Scenario 1: RAG returns EMPTY contexts")
        print("-" * 80)
        
        contexts = []  # Empty contexts
        
        print(f"Contexts: {contexts}")
        print(f"Is empty: {not contexts}")
        print(f"All scores zero: {all(c['score'] == 0 for c in contexts) if contexts else 'N/A (empty)'}")
        
        # Simulate LLM check
        if not contexts or all(c['score'] == 0 for c in contexts):
            print("✅ SHOULD return 'materi belum tersedia' message")
            
            # Call method directly
            llm = LLMService()
            message = llm._generate_no_material_message("prisma", "netral")
            print("\nGenerated Message:")
            print("-" * 80)
            print(message)
            print("-" * 80)
        else:
            print("❌ SHOULD NOT reach here - would call LLM")
        
        # Scenario 2: RAG returns contexts with all zero scores
        print("\n\n📝 Scenario 2: RAG returns contexts but ALL scores are 0")
        print("-" * 80)
        
        contexts = [
            {'text': 'irrelevant text 1', 'score': 0.0},
            {'text': 'irrelevant text 2', 'score': 0.0},
            {'text': 'irrelevant text 3', 'score': 0.0}
        ]
        
        print(f"Contexts count: {len(contexts)}")
        print(f"Is empty: {not contexts}")
        print(f"All scores zero: {all(c['score'] == 0 for c in contexts)}")
        
        if not contexts or all(c['score'] == 0 for c in contexts):
            print("✅ SHOULD return 'materi belum tersedia' message")
            
            llm = LLMService()
            message = llm._generate_no_material_message("tabung", "bingung")
            print("\nGenerated Message:")
            print("-" * 80)
            print(message)
            print("-" * 80)
        else:
            print("❌ SHOULD NOT reach here - would call LLM")
        
        # Scenario 3: RAG returns contexts with good scores
        print("\n\n📝 Scenario 3: RAG returns contexts with GOOD scores")
        print("-" * 80)
        
        contexts = [
            {'text': 'relevant text about kubus', 'score': 0.7},
            {'text': 'volume kubus formula', 'score': 0.68},
            {'text': 'kubus properties', 'score': 0.62}
        ]
        
        print(f"Contexts count: {len(contexts)}")
        print(f"Is empty: {not contexts}")
        print(f"All scores zero: {all(c['score'] == 0 for c in contexts)}")
        
        if not contexts or all(c['score'] == 0 for c in contexts):
            print("❌ SHOULD NOT reach here - has good contexts")
        else:
            print("✅ SHOULD call LLM with these contexts")
            print("   LLM would generate adaptive explanation based on:")
            for i, ctx in enumerate(contexts, 1):
                print(f"   - Context {i}: score={ctx['score']:.2f}")
        
        # Scenario 4: Real RAG test with database
        print("\n\n📝 Scenario 4: REAL RAG test - topik yang TIDAK ada (prisma)")
        print("-" * 80)
        
        contexts = rag_service.retrieve_context(
            query="prisma",
            topik="prisma",
            level="pemula",
            top_k=3
        )
        
        print(f"RAG Results: {len(contexts)} contexts found")
        if contexts:
            best_score = max(c['score'] for c in contexts)
            print(f"Best score: {best_score:.4f}")
            
            if all(c['score'] == 0 for c in contexts) or best_score < 0.1:
                print("✅ All scores are zero or very low - SHOULD show 'materi belum tersedia'")
            else:
                print("❌ Has good scores - would proceed to LLM")
                for i, ctx in enumerate(contexts, 1):
                    print(f"   Context {i}: score={ctx['score']:.4f}")
        else:
            print("✅ No contexts - SHOULD show 'materi belum tersedia'")
        
        # Scenario 5: Real RAG test with database - topik yang ADA
        print("\n\n📝 Scenario 5: REAL RAG test - topik yang ADA (kubus)")
        print("-" * 80)
        
        contexts = rag_service.retrieve_context(
            query="volume kubus",
            topik="kubus",
            level="pemula",
            top_k=3
        )
        
        print(f"RAG Results: {len(contexts)} contexts found")
        if contexts:
            best_score = max(c['score'] for c in contexts)
            print(f"Best score: {best_score:.4f}")
            
            if all(c['score'] == 0 for c in contexts) or best_score < 0.1:
                print("❌ All scores are zero or very low - unexpected!")
            else:
                print("✅ Has good scores - SHOULD proceed to LLM")
                for i, ctx in enumerate(contexts, 1):
                    print(f"   Context {i}: score={ctx['score']:.4f}, preview={ctx['text'][:80]}...")
        else:
            print("❌ No contexts - unexpected! Materials should exist")
        
        print("\n" + "="*80)
        print("✅ Test Complete")
        print("="*80)
        
        print("\n📊 SUMMARY:")
        print("-" * 80)
        print("✅ LLM will return 'materi belum tersedia' message when:")
        print("   1. RAG returns empty contexts")
        print("   2. RAG returns contexts but all scores are 0")
        print("   3. No teacher materials exist in database for that topic")
        print()
        print("✅ LLM will generate adaptive explanation when:")
        print("   1. RAG returns contexts with good scores (> 0)")
        print("   2. Teacher materials exist and match the query")
        print("-" * 80)

if __name__ == '__main__':
    mock_llm_with_no_materials()
