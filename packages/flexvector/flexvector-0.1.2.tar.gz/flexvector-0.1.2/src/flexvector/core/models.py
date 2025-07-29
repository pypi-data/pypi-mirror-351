import abc
from typing import List, Dict, Any, Optional, Union

from langchain_core.documents import Document as LangChainDocument


class Document(LangChainDocument):
    pass


class VectorDBClient(metaclass=abc.ABCMeta):
    """Abstract base class for vector database clients."""

    @abc.abstractmethod
    def load(self, collection_name: str, **kwargs) -> list[Document]:
        """Load data into the vector database."""
        pass

    @abc.abstractmethod
    async def load_async(self, collection_name: str, **kwargs) -> list[Document]:
        """Load data into the vector database asynchronously."""
        pass

    def ingest(self, collection_name: str, **kwargs) -> List[Document]:
        return self.load(collection_name, **kwargs)

    async def ingest_async(self, collection_name: str, **kwargs) -> List[Document]:
        return await self.load_async(collection_name, **kwargs)
    
    @abc.abstractmethod
    async def from_langchain(self, collection_name: str, documents: Union[List[Document], List[LangChainDocument]], **kwargs) -> List[Document]:
        """Load langchain compatible documents into the vector database."""
        pass

    @abc.abstractmethod
    def remove_collection(self, collection_name: str) -> None:
        pass

    @abc.abstractmethod
    async def remove_collection_async(self, collection_name: str) -> None:
        pass

    @abc.abstractmethod
    def delete(self, collection_name: str, ids: List[str]) -> None:
        """Delete a list of documents from the vector database."""
        pass

    @abc.abstractmethod
    async def delete_async(self, collection_name: str, ids: List[str]) -> None:
        """Delete a list of documents from the vector database asynchronously."""
        pass

    @abc.abstractmethod
    def search(
            self,
            collection_name: str,
            query: Union[str, List[float]],
            top_k: int = 3,
            filters: Optional[Dict[str, Any]] = None,
            **kwargs: Any
    ) -> List[Document]:
        """Search the vector database."""
        pass

    @abc.abstractmethod
    async def search_async(
            self,
            collection_name: str,
            query: Union[str, List[float]],
            top_k: int = 3,
            filters: Optional[Dict[str, Any]] = None,
            **kwargs: Any
    ) -> List[Document]:
        """Search the vector database asynchronously."""
        pass

    @abc.abstractmethod
    def exists(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database."""
        pass

    @abc.abstractmethod
    async def exists_async(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database asynchronously."""
        pass

    def get_info(self):
        return {}

    async def get_info_async(self):
        return {}

    @property
    @abc.abstractmethod
    def langchain(self):
        """Return a LangChain compatible client."""
        pass

    @property
    @abc.abstractmethod
    def llama_index(self):
        """Return a LlamaIndex compatible client."""
        pass
