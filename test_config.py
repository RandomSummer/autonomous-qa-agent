from backend.config import settings

# Test 1: Validate settings
try:
    settings.validate()
    print("✓ Config validated successfully")
except ValueError as e:
    print(f"✗ Config error: {e}")

# Test 2: Create directories
settings.create_directories()

# Test 3: Print key settings
print(f"\n📊 Settings Summary:")
print(f"  LLM Model: {settings.LLM_MODEL}")
print(f"  Embedding Model: {settings.EMBEDDING_MODEL}")
print(f"  Chunk Size: {settings.CHUNK_SIZE}")
print(f"  Upload Path: {settings.UPLOAD_PATH}")
print(f"  Vector DB Path: {settings.VECTOR_DB_PATH}")