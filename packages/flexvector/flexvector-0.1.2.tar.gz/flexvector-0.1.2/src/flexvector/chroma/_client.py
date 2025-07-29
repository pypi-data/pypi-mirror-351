import hashlib
import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from typing import List, Dict, Any, Union

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from tqdm import tqdm

from flexvector.config import VectorDBSettings
from flexvector.core import VectorDBClient, Document


class ChromaFlexClient(VectorDBClient):
    __slots__ = (
        "_chroma_client",
        "_embeddings",
        "logger",
        "config",

    )
    def __init__(self, config: VectorDBSettings):
        self.logger = logger.bind(context="ChromaClientSync")
        self.config = config
        if any([key is None for key in [config.CHROMA_HTTP_URL, config.CHROMA_API_KEY]]):
            logger.info("CHROMA http url and api key not provided, assuming local instance")
            self._chroma_client = chromadb.Client(settings=chromadb.Settings(
                is_persistent=True,
                persist_directory=config.CHROMA_DB_FILE,
            ))
        else:
            logger.info("Connecting to remote Chroma instance")
            self._chroma_client = chromadb.HttpClient(
                host=config.CHROMA_HTTP_URL,
                port=config.CHROMA_HTTP_PORT,
                settings=chromadb.Settings(
                    # See: https://cookbook.chromadb.dev/running/running-chroma/
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                    chroma_client_auth_credentials=config.CHROMA_API_KEY
                )
            )
        self._chroma_client.count_collections()
        self.logger.info(
            f"Successfully connected to Chroma instance at {config.CHROMA_HTTP_URL or config.CHROMA_DB_FILE}")
        self._embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY,
                                            dimensions=config.EMBEDDING_DIMENSION,
                                            chunk_size=3096,
                                            show_progress_bar=True,
                                            model=config.EMBEDDING_MODEL)
        self.logger.debug(f"Using embedding model {config.EMBEDDING_MODEL}")

    def load(self, collection_name: str, **kwargs) -> list[Document]:
        """Load data into a chroma db collection.

        Args:
            collection_name (str): The name of the collection to load data into.
            **kwargs: Additional arguments to specify the source of the data. Can be:
                - path (str or list): Path(s) to the data file(s).
                - data (list): List of documents to load.
                - uri (str or list): URI(s) to fetch data from.
        """

        self.logger.debug(f"Loading to collection {collection_name} given kwargs: {kwargs.keys()}")

        path = kwargs.get("path")
        data = kwargs.get("data")
        uri = kwargs.get("uri")

        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings,
            client=self._chroma_client,
            create_collection_if_not_exists=True,
            collection_metadata=dict(
                model=self._embeddings.model,
                dimensions=self.config.EMBEDDING_DIMENSION,
                lastUpdate=datetime.now(UTC).isoformat(),
                class_="langchain_chroma.Chroma",
            )
        )

        if path:
            return self._load_from_path(vectorstore, path)
        elif data:
            return self._load_from_data(vectorstore, data)
        elif uri:
            return self._load_from_uri(vectorstore, uri)
        else:
            raise ValueError("You MUST provide either path, data, or uri to load data")

    def from_langchain(self, collection_name: str, documents: List[Document], **kwargs) -> list[Document]:
        """Load langchain compatible documents into the vector database.

        Args:
            collection_name (str): The name of the collection to load data into.
            documents (List[Document]): List of langchain compatible documents to load.
            **kwargs: Additional arguments for loading data.
        """
        self.logger.debug(f"Loading {len(documents)} langchain documents into collection {collection_name}...")
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings,
            client=self._chroma_client,
            create_collection_if_not_exists=True
        )
        ids = vectorstore.add_documents(documents)
        self.logger.info(f"Loaded {len(ids)} documents into collection {collection_name}.")
        return documents

    def search(self, collection_name: str, query: str, top_k: int = 3, **kwargs) -> List[Document]:
        """Search a Chroma collection for similar documents.

        Args:
            collection_name (str): The name of the collection to search.
            query (str): The query string or vector to search for.
            top_k (int): The number of top results to return.
            **kwargs: Additional arguments for the search.
        Returns:
            List[Document]: A list of documents matching the query.
        """
        self.logger.debug(f"Searching collection {collection_name} with query: {query[:25]}...")
        self.logger.debug("Given kwargs: ", kwargs)

        search_type = kwargs.get("search_type", "mmr")
        filters = kwargs.get("filters", {})
        initial_candidates = kwargs.get("initial_candidates", 10)  # Before re-ranking
        self.logger.debug(
            f"Search params: search_type={search_type}, filters={filters}, initial_candidates={initial_candidates}")

        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings,
            client=self._chroma_client,
            create_collection_if_not_exists=False
        )

        retriever = vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": top_k, "fetch_k": initial_candidates},
        )
        docs = retriever.invoke(query, filter=filters if len(filters) > 0 else None)
        self.logger.debug(f"Found {len(docs)} documents for query {query[:25]}...")
        return docs

    def remove_collection(self, collection_name: str) -> None:
        """Remove a collection from Chroma.

        Args:
            collection_name (str): The name of the collection to remove.
        """
        self.logger.debug(f"Removing collection {collection_name}...")
        self._chroma_client.delete_collection(collection_name)
        self.logger.info(f"Collection {collection_name} removed.")

    def delete(self, collection_name: str, ids: List[str]) -> None:
        """Delete a list of documents from a Chroma collection.

        Args:
            collection_name (str): The name of the collection to delete from.
            ids (List[str]): List of document IDs to delete.
        """
        self.logger.debug(f"Deleting {len(ids)} documents from collection {collection_name}...")
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings,
            client=self._chroma_client,
            create_collection_if_not_exists=False
        )
        vectorstore.delete(ids)
        self.logger.info(f"Deleted {len(ids)} documents from collection {collection_name}.")

    def exists(self, collection_name: str) -> bool:
        """Check if a collection exists in Chroma.

        Args:
            collection_name (str): The name of the collection to check.
        Returns:
            bool: True if the collection exists, False otherwise.
        """
        self.logger.debug(f"Checking if collection {collection_name} exists...")
        try:
            _ = self._chroma_client.get_collection(collection_name)
            exists = True
        except ValueError:
            exists = False
        self.logger.info(f"Collection {collection_name} exists: {exists}")
        return exists

    def get_info(self):
        return dict(
            connection=self.config.CHROMA_HTTP_URL or self.config.CHROMA_DB_FILE,
            collections={
                "count": self._chroma_client.count_collections(),
                "names": self._chroma_client.list_collections()
            },
            version=self._chroma_client.get_version(),
            meta={
                "settings": self._chroma_client.get_settings(),
            }
        )

    @property
    def client(self) -> Union[chromadb.Client, chromadb.HttpClient]:
        return self._chroma_client

    @property
    def langchain(self) -> Chroma:
        return Chroma(
            embedding_function=self._embeddings,
            client=self._chroma_client,
            create_collection_if_not_exists=False
        )

    @property
    def llama_index(self):
        try:
            from llama_index.vector_stores import ChromaVectorStore

            return ChromaVectorStore(chroma_client=self._chroma_client)
        except ImportError:
            self.logger.error("llama-index-vector-stores is not installed. Please install it to use this feature.")
            raise

    # region Helper methods
    def _get_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def _load_from_path(self, vectorstore: Chroma, paths: Union[str, List[str]]) -> list[Document]:
        """Load data from a file or list of files into chroma db collection. The path could also be a directory.

        Args:
            vectorstore (Chroma): The langchain Chroma vector store instance.
            paths (Union[str, List[str]]): Path(s) to the data file(s) or directory(s) to load data from.

        Returns:
            list[Document]: A list of documents loaded from the specified path(s).
        """
        self.logger.debug(f"Begin loading data from {len(paths)} file(s)...")
        try:
            from langchain_community.document_loaders import DirectoryLoader
        except ImportError:
            self.logger.error("langchain-community package is not installed. Please install it to use this feature.")
            raise

        try:
            from langchain_docling import DoclingLoader
        except ImportError:
            self.logger.error("langchain-docling package is not installed. Please install it to use this feature.")
            raise

        from langchain_community.document_loaders import DirectoryLoader
        from langchain_docling import DoclingLoader

        if isinstance(paths, str):
            paths = [paths]

        self.logger.debug("Moving files to a single tmp directory...")
        with tempfile.TemporaryDirectory(suffix="_chroma_loader_tmp", delete=True) as tmp_dir:
            for path in tqdm(paths, desc="Moving to tmp directory", unit="path"):
                if os.path.isdir(path):
                    self.logger.debug(f"Copying directory {path} to {tmp_dir}")
                    shutil.copytree(path, os.path.join(tmp_dir, os.path.basename(path)))
                else:
                    self.logger.debug(f"Copying file {path} to {tmp_dir}")
                    shutil.copy2(path, tmp_dir)

            # If any files, have .txt or .text extension, rename them to .md
            for file in os.listdir(tmp_dir):
                if file.endswith(".txt") or file.endswith(".text"):
                    new_file = os.path.splitext(file)[0] + ".md"
                    os.rename(os.path.join(tmp_dir, file), os.path.join(tmp_dir, new_file))
                    self.logger.debug(f"Renamed {file} to {new_file}")

            self.logger.debug(f"Loading data from {tmp_dir}...")
            # noinspection PyTypeChecker
            loader = DirectoryLoader(tmp_dir, loader_cls=DoclingLoader)
            documents = []
            for d in loader.load():
                meta = d.metadata
                meta["model"] = self._embeddings.model
                meta["dimensions"] = self.config.EMBEDDING_DIMENSION
                meta["lastUpdate"] = datetime.now(UTC).isoformat()
                for key, value in meta.items():
                    if isinstance(value, (dict, list)):
                        self.logger.debug(f"Converting metadata={key}:{value} to str")
                        meta[key] = json.dumps(value, indent=2)
                d.metadata = meta
                documents.append(d)
            vectorstore.add_documents(documents)
            self.logger.info(f"Loaded {len(documents)} documents from {tmp_dir}")
            return documents

    def _load_from_data(self, vectorstore: Chroma, data: List[Dict[str, Any]]) -> list[Document]:
        """Loads data from a list of dictionaries into a Chroma collection.

        Args:
            vectorstore (Chroma): The langchain Chroma vector store instance.
            data (List[Dict[str, Any]]): List of dictionaries containing the data to load.

        Returns:
            list[Document]: A list of documents loaded from the specified data.
        """
        self.logger.debug(f"Loading {len(data)} objects into chroma collection...")
        documents = []
        try:
            for item in tqdm(data, desc="Transforming to documents", unit="dict"):
                # noinspection PyArgumentList
                doc = Document(
                    page_content=item["content"],
                    id=self._get_hash(item["content"]),
                    metadata=dict(
                        model=self._embeddings.model,
                        dimensions=self.config.EMBEDDING_DIMENSION,
                        lastUpdate=datetime.now(UTC).isoformat(),
                        **item.get("metadata", {})
                    )
                )
                documents.append(doc)
        except KeyError as e:
            self.logger.error(
                f"Key error while loading data: {e}. Please make sure content key is present in the data.")
            raise

        ids = vectorstore.add_documents(documents)
        self.logger.debug(f"Loaded {len(ids)} documents")
        return documents

    def _load_from_uri(self, vectorstore: Chroma, uris: Union[str, List[str]]) -> list[Document]:
        """Load data from a list of URIs into a Chroma collection.
        Each URI must be a publicly accessible document supported by `docling` loaders.

        Args:
            vectorstore (Chroma): The langchain Chroma vector store instance.
            uris (Union[str, List[str]]): URI(s) to fetch data from.

        Returns:
            list[Document]: A list of documents loaded from the specified URIs.
        """
        try:
            from langchain_docling import DoclingLoader
        except ImportError:
            self.logger.error("langchain-docling package is not installed. Please install it to use this feature.")
            raise

        if isinstance(uris, str):
            uris = [uris]

        self.logger.debug(f"Loading {len(uris)} URIs into chroma collection...")
        documents = []
        loader = DoclingLoader(file_path=uris)
        for doc in tqdm(loader.load(), desc="Enrich Metatata", unit="doc"):
            meta = doc.metadata
            meta["model"] = self._embeddings.model
            meta["dimensions"] = self.config.EMBEDDING_DIMENSION
            meta["lastUpdate"] = datetime.now(UTC).isoformat()
            documents.append(doc)

        ids = vectorstore.add_documents(documents)
        self.logger.debug(f"Loaded {len(ids)} documents")
        return documents


    # endregion

    # region: Default async methods

    async def remove_collection_async(self, collection_name: str) -> None:
        raise NotImplementedError("Async operations are not supported in this client.")

    async def delete_async(self, collection_name: str, ids: List[str]) -> None:
        raise NotImplementedError("Async operations are not supported in this client.")

    async def search_async(self, collection_name: str, query: str, top_k: int = 3, **kwargs) -> List[Document]:
        raise NotImplementedError("Async operations are not supported in this client.")

    async def load_async(self, collection_name: str, **kwargs) -> list[Document]:
        raise NotImplementedError("Async operations are not supported in this client.")

    async def exists_async(self, collection_name: str) -> bool:
        raise NotImplementedError("Async operations are not supported in this client.")
    # endregion
