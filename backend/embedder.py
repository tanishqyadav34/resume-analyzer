import chromadb
from fastembed import TextEmbedding

# Load once at module level — uses ONNX, no PyTorch, ~100MB RAM
embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
chroma_client = chromadb.Client()

def embed_and_store(chunks: list[str], collection_name: str = "resume"):
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass
    
    collection = chroma_client.create_collection(collection_name)
    embeddings = list(embedding_model.embed(chunks))
    embeddings_list = [e.tolist() for e in embeddings]
    
    collection.add(
        documents=chunks,
        embeddings=embeddings_list,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection

def retrieve_relevant_chunks(collection, query: str, n_results: int = 5) -> list[str]:
    query_embedding = list(embedding_model.embed([query]))[0].tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count())
    )
    return results["documents"][0]
