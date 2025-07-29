import argparse
import sys
import time
from typing import List, Dict, Any

from flexvector.config import settings as default_config, config_manager
from flexvector.core.models import Document, VectorDBClient
from flexvector.factory import VectorDBFactory
from loguru import logger


def create_sample_config(file_path: str, format_: str):
    """Create a sample configuration file."""
    logger.info(f"Creating sample configuration file: {file_path}")
    try:
        config_manager.create_sample_config(file_path, format_)
        logger.success(f"Sample configuration file created: {file_path}")
    except Exception as e:
        logger.error(f"Failed to create sample config: {e}")
        sys.exit(1)


def get_config_from_args(args) -> Dict[str, Any]:
    """Extract configuration overrides from CLI arguments."""
    overrides = {}
    
    # Map CLI args to config field names
    if hasattr(args, 'chroma_url') and args.chroma_url:
        overrides['CHROMA_HTTP_URL'] = args.chroma_url
    if hasattr(args, 'qdrant_url') and args.qdrant_url:
        overrides['QDRANT_HTTP_URL'] = args.qdrant_url
    if hasattr(args, 'weaviate_url') and args.weaviate_url:
        overrides['WEAVIATE_HTTP_URL'] = args.weaviate_url
    if hasattr(args, 'embedding_model') and args.embedding_model:
        overrides['EMBEDDING_MODEL'] = args.embedding_model
    if hasattr(args, 'openai_api_key') and args.openai_api_key:
        overrides['OPENAI_API_KEY'] = args.openai_api_key
    
    return overrides


def load_data(db_instance: VectorDBClient, input_path: str, collection_name: str):
    logger.info(f"Loading data from {input_path} into collection '{collection_name}'")
    return db_instance.load(collection_name=collection_name, path=input_path)


def query_data(db_instance: VectorDBClient, query: str, collection_name: str, top_k: int = 3):
    results = db_instance.search(
        collection_name=collection_name,
        query=query,
        top_k=top_k
    )
    return results


def delete_collection(db_instance: VectorDBClient, collection_name: str):
    logger.info(f"Deleting collection '{collection_name}'")
    try:
        db_instance.remove_collection(collection_name)
        logger.success(f"Collection '{collection_name}' deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete collection: {e}")
        sys.exit(1)


def _display_results(results: List[Document]):
    if not results:
        logger.warning("No results found")
        return
    
    logger.info(f"Found {len(results)} results:")
    for i, doc in enumerate(results):
        content = doc.page_content
        # Truncate content if it's too long
        if len(content) > 300:
            content = content[:297] + "..."
            
        logger.info(f"\nResult {i+1}:")
        logger.info(f"Content: {content}")
        logger.info(f"Metadata: {doc.metadata}")
        logger.info("-" * 50)


def main():
    if args.verbose:
        logger.level("DEBUG")
    else:
        logger.level("INFO")

    # Handle config operations first
    if args.operation == "init-config":
        create_sample_config(args.config_file, args.config_format)
        return

    # Load configuration from multiple sources
    cli_overrides = get_config_from_args(args)
    try:
        config = config_manager.load_settings(
            config_file=args.config_file,
            cli_overrides=cli_overrides,
            environment=args.environment
        )
        logger.debug(f"Configuration loaded successfully")
        if args.verbose:
            # Log key config values (excluding sensitive data)
            logger.debug(f"Database type: {args.db_type}")
            logger.debug(f"Embedding model: {config.EMBEDDING_MODEL}")
            logger.debug(f"Environment: {args.environment or 'default'}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.info("Falling back to default configuration")
        config = default_config

    logger.info(f"Running Operation: {args.operation}")
    start = time.perf_counter()
    db_instance = VectorDBFactory.get(args.db_type, config)

    if args.operation == "load":
        if args.input_file:
            load_data(db_instance, args.input_file, args.collection)
        elif args.input_dir:
            load_data(db_instance, args.input_dir, args.collection)
        else:
            logger.error("Please provide either input file or input directory")
            sys.exit(1)
        logger.info(f"Data loaded successfully into collection '{args.collection}'! Time taken: {time.perf_counter() - start:.2f} seconds")
    
    elif args.operation == "search":
        if not args.query:
            logger.error("Please provide a search query")
            sys.exit(1)
        results = query_data(db_instance, args.query, args.collection, args.top_k)
        _display_results(results)
        logger.info(f"Search completed in {time.perf_counter() - start:.2f} seconds")
    
    elif args.operation == "delete":
        delete_collection(db_instance, args.collection)
        logger.info(f"Operation completed in {time.perf_counter() - start:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="flexvector CLI - Tool for interacting with flexvector stores",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        "operation",
        choices=["load", "search", "delete", "init-config"],
        help="Operation to perform:\n"
             "  load        - Load data into a flexvector collection\n"
             "  search      - Search for similar documents in a flexvector collection\n"
             "  delete      - Delete a flexvector collection\n"
             "  init-config - Create a sample configuration file"
    )
    
    # Database configuration
    parser.add_argument(
        "--db-type", "-t",
        choices=["chroma", "qdrant", "weaviate", "pg"],
        default="chroma",
        help="flexvector store type (default: chroma)"
    )
    
    parser.add_argument(
        "--collection", "-c",
        type=str,
        default="default",
        help="Collection name (default: default)"
    )
    
    # Input options for load operation
    parser.add_argument(
        "--input-file", "-i",
        type=str,
        help="Input file path (for load operation)"
    )
    
    parser.add_argument(
        "--input-dir", "-d",
        type=str,
        help="Input directory path (for load operation)"
    )
    
    # Search options
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Search query (for search operation)"
    )
    
    parser.add_argument(
        "--top-k",
        "-k",
        type=int,
        default=3,
        help="Number of results to return (default: 3)"
    )
    
    # Other options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Configuration management options
    parser.add_argument(
        "--config-file", "-f",
        type=str,
        help="Path to configuration file (YAML, TOML, or JSON)"
    )
    
    parser.add_argument(
        "--environment", "-e",
        type=str,
        help="Environment name (dev, staging, prod) for environment-specific settings"
    )
    
    parser.add_argument(
        "--config-format",
        choices=["yaml", "toml", "json"],
        default="yaml",
        help="Format for configuration file when using init-config (default: yaml)"
    )
    
    # Configuration overrides (highest priority)
    config_group = parser.add_argument_group('Configuration Overrides')
    config_group.add_argument(
        "--chroma-url",
        type=str,
        help="Override Chroma HTTP URL"
    )
    config_group.add_argument(
        "--qdrant-url", 
        type=str,
        help="Override Qdrant HTTP URL"
    )
    config_group.add_argument(
        "--weaviate-url",
        type=str, 
        help="Override Weaviate HTTP URL"
    )
    config_group.add_argument(
        "--embedding-model",
        type=str,
        help="Override embedding model"
    )
    config_group.add_argument(
        "--openai-api-key",
        type=str,
        help="Override OpenAI API key"
    )
    
    args = parser.parse_args()
    
    # Validate operation-specific arguments
    if args.operation == "load" and not (args.input_file or args.input_dir):
        parser.error("The load operation requires either --input-file or --input-dir")
    
    if args.operation == "search" and not args.query:
        parser.error("The search operation requires --query")
    
    if args.operation == "init-config" and not args.config_file:
        parser.error("The init-config operation requires --config-file")
    
    main()


# Examples:

# # Create a sample configuration file
# python cli.py init-config --config-file flexvector.yaml --config-format yaml

# # Load documents using default configuration
# python cli.py load --input-file examples/files/data.txt --collection my_documents --verbose

# # Load documents using custom configuration file
# python cli.py load --input-dir examples/files --collection research_papers --config-file config/prod.yaml --verbose

# # Load documents with environment-specific settings
# python cli.py load --input-dir examples/files --collection research_papers --config-file flexvector.yaml --environment production --verbose

# # Search with configuration overrides
# python cli.py search --query "What is vector database?" --collection my_documents --top-k 5 --chroma-url http://localhost:8000 --verbose

# # Search with custom embedding model
# python cli.py search --query "machine learning" --collection research_papers --embedding-model text-embedding-ada-002 --verbose

# # Delete a collection
# python cli.py delete --collection my_documents --verbose
