from flexvector.config import VectorDBSettings
from flexvector.core.models import VectorDBClient


class VectorDBFactory:

    @staticmethod
    def chroma(config: VectorDBSettings) -> VectorDBClient:
        from flexvector.chroma import ChromaFlexClient

        return ChromaFlexClient(config)

    @staticmethod
    def qdrant(config: VectorDBSettings) -> VectorDBClient:
        from flexvector.qdrant import QdrantFlexClient

        return QdrantFlexClient(config)

    @staticmethod
    def weaviate(config: VectorDBSettings) -> VectorDBClient:
        from flexvector.weaviate import WeaviateFlexClient

        return WeaviateFlexClient(config)

    @staticmethod
    def pgvector(config: VectorDBSettings) -> VectorDBClient:
        from flexvector.pgvector import PostgresFlexClient

        return PostgresFlexClient(config)

    @staticmethod
    def get(db_type: str, config: VectorDBSettings) -> VectorDBClient:
        factory = VectorDBFactory()
        if db_type == "chroma":
            return factory.chroma(config)
        elif db_type == "qdrant":
            return factory.qdrant(config)
        elif db_type == "weaviate":
            return factory.weaviate(config)
        elif db_type == "pg":
            return factory.pgvector(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def list_available() -> list[str]:
        return [
            "chroma",
            "qdrant",
            "weaviate",
            "pg",
        ]
