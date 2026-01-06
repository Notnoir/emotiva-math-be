"""
Test RAG Service with uploaded files
"""
from app import create_app
from app.rag_service import RAGService

app = create_app()
app.app_context().push()

print("="*60)
print("Testing RAG Service with Uploaded Files")
print("="*60)

rag = RAGService()
rag.reload_materials()

print("\n" + "="*60)
print("Testing retrieval for 'limas'")
print("="*60)

results = rag.retrieve_context('limas', top_k=2)

for i, result in enumerate(results):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Score: {result['score']:.4f}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Material: {result['metadata']['judul']} ({result['metadata']['topik']})")
    print(f"Text preview: {result['text'][:300]}...")

print("\n" + "="*60)
print("Testing retrieval for 'volume kubus'")
print("="*60)

results = rag.retrieve_context('volume kubus', top_k=2)

for i, result in enumerate(results):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Score: {result['score']:.4f}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Material: {result['metadata']['judul']} ({result['metadata']['topik']})")
    print(f"Text preview: {result['text'][:300]}...")
