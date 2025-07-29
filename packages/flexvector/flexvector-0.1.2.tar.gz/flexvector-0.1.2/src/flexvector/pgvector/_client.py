import asyncio
import hashlib
import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from typing import List, Dict, Any, Union

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from loguru import logger
from sqlalchemy import text
from tqdm import tqdm

from flexvector.config import VectorDBSettings
from flexvector.core import VectorDBClient, Document


class PostgresFlexClient(VectorDBClient):
    __slots__ = (
        "_postgres_client",
        "_embeddings",
        "logger",
        "config",

    )
    def __init__(self, config: VectorDBSettings):
        self.logger = logger.bind(context="PostgresFlexClient")
        self.config = config
        if any([key is None for key in [config.PG_VECTOR_CONNECTION]]):
            raise ValueError("You MUST provide a valid connection string to connect to the database.")
        # CONNECTION_STRING = "postgresql+psycopg3://langchain:langchain@localhost:6024/langchain"
        self._postgres_client = lambda url: PGEngine.from_connection_string(url=url)
        self._embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY,
                                            dimensions=config.EMBEDDING_DIMENSION,
                                            chunk_size=3096,
                                            show_progress_bar=True,
                                            model=config.EMBEDDING_MODEL)
        self.logger.debug(f"Using embedding model {config.EMBEDDING_MODEL}")

    def load(self, collection_name: str, **kwargs) -> list[Document]:
        """Load data into a PostgreSQL vector table.

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

        engine = self._get_or_create_collection(collection_name, **kwargs)
        vectorstore = PGVectorStore.create_sync(
            engine=engine,
            table_name=collection_name,
            embedding_service=self._embeddings,
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

        engine = self._get_or_create_collection(collection_name, **kwargs)
        vectorstore = PGVectorStore.create_sync(
            engine=engine,
            table_name=collection_name,
            embedding_service=self._embeddings,
        )
        ids = vectorstore.add_documents(documents)
        self.logger.info(f"Loaded {len(ids)} documents into collection {collection_name}.")
        return documents

    def _get_or_create_collection(self, collection_name: str, **kwargs):
        engine = self._postgres_client(self.config.PG_VECTOR_CONNECTION)
        engine.init_vectorstore_table(
            table_name=collection_name,
            vector_size=self.config.EMBEDDING_DIMENSION,
            schema_name="vectorstore",
            overwrite_existing=kwargs.get("overwrite_existing", False),
        )
        return engine

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

        engine = self._get_or_create_collection(collection_name, **kwargs)
        vectorstore = PGVectorStore.create_sync(
            engine=engine,
            table_name=collection_name,
            embedding_service=self._embeddings,
        )

        retriever = vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": top_k, "fetch_k": initial_candidates},
        )
        docs = retriever.invoke(query, filter=filters if len(filters) > 0 else None)
        self.logger.debug(f"Found {len(docs)} documents for query {query[:25]}...")
        return docs

    @staticmethod
    async def _run_query(query, engine: PGEngine):
        """Run a SQL query against the database engine.
        
        Args:
            query: SQL query to run, can be a string or a SQLAlchemy text object with bound parameters
            engine: The database engine to run the query against
        """
        logger.debug(f"Running query: {str(query)[:50]}")
        # noinspection PyProtectedMember
        async with engine._pool.connect() as conn:
            result = await conn.execute(query)
            await conn.commit()
        return result

    def remove_collection(self, collection_name: str) -> None:
        """Remove a collection from PostgreSQL.

        Args:
            collection_name (str): The name of the collection to remove.
        """
        self.logger.debug(f"Removing collection {collection_name}...")
        engine = self._postgres_client(self.config.PG_VECTOR_CONNECTION)
        asyncio.run(
            self._run_query(
                text(f"DROP TABLE IF EXISTS vectorstore.{collection_name} CASCADE"),
                engine=engine,
            )
        )
        self.logger.info(f"Collection {collection_name} removed.")

    def delete(self, collection_name: str, ids: List[str]) -> None:
        """Delete a list of documents from a PostgreSQL collection.

        Args:
            collection_name (str): The name of the collection to delete from.
            ids (List[str]): List of document IDs to delete.
        """
        self.logger.debug(f"Deleting {len(ids)} documents from collection {collection_name}...")
        engine = self._postgres_client(self.config.PG_VECTOR_CONNECTION)
        vectorstore = PGVectorStore.create_sync(
            engine=engine,
            table_name=collection_name,
            embedding_service=self._embeddings,
        )
        vectorstore.delete(ids)
        self.logger.info(f"Deleted {len(ids)} documents from collection {collection_name}.")

    def exists(self, collection_name: str) -> bool:
        """Check if a collection exists in PostgreSQL.

        Args:
            collection_name (str): The name of the collection to check.
        Returns:
            bool: True if the collection exists, False otherwise.
        """
        self.logger.debug(f"Checking if collection {collection_name} exists...")
        engine = self._postgres_client(self.config.PG_VECTOR_CONNECTION)

        result = asyncio.run(
            self._run_query(
                query=text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :table_name AND table_schema = 'vectorstore')").bindparams(table_name=collection_name),
                engine=engine, )
        )

        exists = result.scalar() if result else False
        self.logger.info(f"Collection {collection_name} exists: {exists}")
        return exists

    def get_info(self):
        """Get information about the PostgreSQL vector database."""
        tables = []
        
        return dict(
            connection=self.config.PG_VECTOR_CONNECTION,
            collections={
                "count": len(tables),
                "names": tables
            },
            meta={
                "embedding_model": self._embeddings.model,
                "embedding_dimensions": self.config.EMBEDDING_DIMENSION,
            }
        )

    @property
    def client(self) -> PGEngine:
        return self._postgres_client(self.config.PG_VECTOR_CONNECTION)

    @property
    def langchain(self) -> PGVectorStore:
        engine = self._get_or_create_collection("default")
        return PGVectorStore.create_sync(
            engine=engine,
            table_name="default",
            embedding_service=self._embeddings,
        )

    @property
    def llama_index(self):
        raise NotImplementedError()

    # region Helper methods
    @staticmethod
    def _get_hash(text_: str) -> str:
        return hashlib.sha256(text_.encode()).hexdigest()

    def _load_from_path(self, vectorstore: PGVectorStore, paths: Union[str, List[str]]) -> list[Document]:
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

    def _load_from_data(self, vectorstore: PGVectorStore, data: List[Dict[str, Any]]) -> list[Document]:
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

    def _load_from_uri(self, vectorstore: PGVectorStore, uris: Union[str, List[str]]) -> list[Document]:
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
        for doc in tqdm(loader.load(), desc="Enrich Metadata", unit="doc"):
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
