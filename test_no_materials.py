"""
Test LLM behavior ketika tidak ada materi dari guru
"""
import os
import sys

# Setup path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Setup environment
os.environ['USE_LLM'] = 'True'
os.environ['GEMINI_API_KEY'] = 'AIzaSyDQkV2j_Ksb5-QLuhsqHcItl6Xa-OcbpG0'
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:@localhost:3306/emotiva-math'

from app import create_app
from app.llm_service import llm_service
from app.rag_service import rag_service

def test_no_materials():
    """Test RAG + LLM behavior ketika tidak ada materi"""
    
    print("\n" + "="*80)
    print("🧪 TEST: LLM Behavior When No Materials Available")
    print("="*80 + "\n")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Test 1: Query topik yang tidak ada materinya
        print("📝 Test 1: Query topik yang tidak ada materinya (prisma)")
        print("-" * 80)
        
        # Check RAG
        contexts = rag_service.retrieve_context(
            query="prisma",
            topik="prisma",
            level="pemula",
            top_k=3
        )
        
        print(f"RAG Results: {len(contexts)} contexts found")
        if contexts:
            for i, ctx in enumerate(contexts, 1):
                print(f"  Context {i}: score={ctx['score']:.4f}, preview={ctx['text'][:100]}...")
        else:
            print("  ❌ No contexts retrieved")
        
        print()
        
        # Test LLM
        result = llm_service.generate_explanation(
            topic="prisma",
            learning_style="visual",
            difficulty="pemula",
            emotion="netral"
        )
        
        print(f"LLM Result Type: {type(result)}")
        print(f"LLM Result Length: {len(result) if result else 0} chars")
        print()
        print("LLM Output:")
        print("-" * 80)
        print(result if result else "None")
        print("-" * 80)
        
        # Test 2: Query topik yang ada materinya
        print("\n\n📝 Test 2: Query topik yang ADA materinya (kubus)")
        print("-" * 80)
        
        # Check RAG
        contexts = rag_service.retrieve_context(
            query="volume kubus",
            topik="kubus",
            level="pemula",
            top_k=3
        )
        
        print(f"RAG Results: {len(contexts)} contexts found")
        if contexts:
            for i, ctx in enumerate(contexts, 1):
                print(f"  Context {i}: score={ctx['score']:.4f}")
        else:
            print("  ❌ No contexts retrieved")
        
        print()
        
        # Test LLM
        result = llm_service.generate_explanation(
            topic="kubus",
            learning_style="visual",
            difficulty="pemula",
            emotion="netral",
            user_query="bagaimana cara menghitung volume kubus?"
        )
        
        print(f"LLM Result Type: {type(result)}")
        print(f"LLM Result Length: {len(result) if result else 0} chars")
        print()
        print("LLM Output (first 500 chars):")
        print("-" * 80)
        if result:
            print(result[:500] + "..." if len(result) > 500 else result)
        else:
            print("None")
        print("-" * 80)
        
        print("\n" + "="*80)
        print("✅ Test Complete")
        print("="*80)

if __name__ == '__main__':
    test_no_materials()
