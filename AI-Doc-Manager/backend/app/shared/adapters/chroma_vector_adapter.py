from typing import Any, Dict, List, Optional

import chromadb

from app.core.config import Settings, get_settings
from app.shared.interfaces import IVectorStore


class ChromaVectorAdapter(IVectorStore):
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        # Connect to ChromaDB (can be configured via settings to use http client or local ephemeral client)
        if hasattr(self.settings, "chroma_host") and self.settings.chroma_host:
            self.client = chromadb.HttpClient(
                host=self.settings.chroma_host, port=getattr(self.settings, "chroma_port", 8000)
            )
        else:
            # Ephemeral memory-based for quick dev testing without external docker if host isn't provided
            self.client = chromadb.EphemeralClient()
            
        collection_name = getattr(self.settings, "chroma_collection", "document_chunks")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert_document(
        self, document_id: str, text_chunks: List[str], embeddings: List[List[float]], metadata: Optional[Dict] = None
    ) -> None:
        if not text_chunks:
            return
            
        ids = [f"{document_id}_{i}" for i in range(len(text_chunks))]
        # Metadata applies to all chunks, or can be individualized
        metadatas = [metadata or {"document_id": document_id} for _ in text_chunks]

        self.collection.upsert(
            documents=text_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def semantic_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        
        matches = []
        if not results["documents"] or not results["documents"][0]:
            return matches

        for doc, meta, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            matches.append({"text": doc, "metadata": meta, "score": distance})
            
        return matches

    def delete_document(self, document_id: str) -> None:
        # Assuming metadata contains document_id, Chroma lets us delete by where clause
        self.collection.delete(where={"document_id": document_id})
