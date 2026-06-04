import uuid
from typing import Any

from google.cloud import aiplatform

from app.core.config import Settings, get_settings
from app.shared.interfaces import IVectorStore


class VertexVectorAdapter(IVectorStore):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        aiplatform.init(
            project=self.settings.gcp_project_id,
            location=getattr(self.settings, "gcp_location", "us-central1")
        )
        # Assumes the Index and IndexEndpoint are already created and deployed.
        self.index_endpoint_id = getattr(self.settings, "vertex_index_endpoint_id", None)
        self.deployed_index_id = getattr(self.settings, "vertex_deployed_index_id", None)
        self.index_id = getattr(self.settings, "vertex_index_id", None)

        if self.index_endpoint_id:
            self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(self.index_endpoint_id)
        if self.index_id:
            self.index = aiplatform.MatchingEngineIndex(self.index_id)

    def upsert_document(
        self, document_id: str, text_chunks: list[str], embeddings: list[list[float]], metadata: dict | None = None
    ) -> None:
        if not text_chunks or not self.index:
            return

        datapoints = []
        for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
            datapoint_id = f"{document_id}_{i}"
            # Vertex AI Vector Search uses Restricts/NumericRestricts for metadata filtering
            # For simplicity, we assume we just index them or use basic metadata if provided
            # A full implementation might serialize metadata into 'restricts'
            datapoints.append(
                aiplatform.matching_engine.matching_engine_index_config.IndexDatapoint(
                    datapoint_id=datapoint_id,
                    feature_vector=embedding,
                    # Note: You can add restricts here for filtering:
                    # restricts=[{"namespace": "document_id", "allow_list": [document_id]}]
                )
            )

        # Upsert to the streaming index
        self.index.upsert_datapoints(datapoints=datapoints)

        # Note: We must also store the text chunk payload somewhere (e.g., GCS, Datastore, or Postgres)
        # because Vertex AI Vector Search only stores vectors and string IDs by default.
        # This is a common pattern: Vector DB returns ID, then you fetch the text from Postgres/GCS.
        # Alternatively, Vertex Vector Search now supports storing small amounts of string data via `crowding_tag` or custom names.

    def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_document_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not self.index_endpoint_id:
            return []

        response = self.index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=top_k,
        )

        matches = []
        if response:
            for neighbor in response[0]:
                # In a real app, neighbor.id is used to fetch the actual text content from the DB
                matches.append({
                    "id": neighbor.id,
                    "score": neighbor.distance,
                    "text": f"Text chunk for {neighbor.id} (needs DB fetch)",
                })
        return matches

    def delete_document(self, document_id: str) -> None:
        # To delete, you typically need to know all the datapoint IDs, or keep a separate record of them.
        # For simplicity, if we know we generated N chunks, we'd loop and delete.
        # Real-world: Query DB to find chunk IDs for the document_id, then delete them from Vertex.
        pass
