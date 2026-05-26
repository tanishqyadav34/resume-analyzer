import chromadb
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()


def embed_and_store(
    chunks: list[str], collection_name: str = "resume"
) -> chromadb.Collection:
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(collection_name)
    embeddings = model.encode(chunks).tolist()
    ids = [f"chunk_{index}" for index in range(len(chunks))]

    collection.add(ids=ids, embeddings=embeddings, documents=chunks)
    return collection


def retrieve_relevant_chunks(collection, query: str, n_results: int = 5) -> list[str]:
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    documents = results.get("documents", [[]])
    return documents[0] if documents else []
