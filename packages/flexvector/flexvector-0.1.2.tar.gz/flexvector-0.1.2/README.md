# [![PyPI Version](https://img.shields.io/pypi/v/flexvector.svg)](https://pypi.org/project/flexvector) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
# Flex Vector

A simple and intuitive vector database abstraction layer supporting multiple vector stores.

![CI](https://github.com/ndamulelonemakh/flexvector/actions/workflows/publish-to-pypi.yml/badge.svg)

## Features

- Unified interface for multiple vector databases
    - [x] Chroma
    - [x] Qdrant
    - [x] Weaviate
    - [x] PGVector
    - [ ] Milvus
    - [ ] Azure AI Search
    - ...and more to come!
- [x] LangChain support
- [ ] LlamaIndex support
- [ ] Flexible data loading from files, direct data, or URIs
- [ ] Async support for all operations
- [x] Command-line interface for common operations



## Installation

```bash
pip install flexvector
```

Add the CLI tool to your path:

```
# After installation, use the 'flexvector' command directly
flexvector --help
```

## Quick Start

### Environment Variables

Required:

```bash
export OPENAI_API_KEY="sk-..."
```

### Using the Python API

```python
from flexvector import VectorDBFactory
from flexvector.config import settings
from flexvector.core import Document

# Initialize client with configuration
client = VectorDBFactory.get("chroma", settings)

# Load documents from file or directory
docs = client.load(collection_name="my_collection", path="path/to/document.txt")

# Or create and add documents directly
from langchain_core.documents import Document

doc = Document(page_content="Hello world", metadata={"source": "example"})
client.from_langchain("my_collection", [doc])

# Search
results = client.search(
    collection_name="my_collection",
    query="hello",
    top_k=5
)

# Delete collection
client.remove_collection("my_collection")

# Delete documents
```

### Using the Command Line Interface

Load documents from a file:
```bash
flexvector load --input-file examples/files/data.txt --collection my_documents

# Or using python
python cli.py load --input-file examples/files/data.txt --collection my_documents
```

Load documents from a directory:
```bash
flexvector load --input-dir examples/files --collection research_papers
```

Search for documents:
```bash
flexvector search --query "What is vector database?" --collection my_documents --top-k 5
```

Delete a collection:
```bash
flexvector delete --collection my_documents
```

## Configuration

FlexVector supports multiple configuration methods for different deployment environments:

### Configuration Sources (in priority order)

1. **CLI arguments** (highest priority) - Direct command-line overrides
2. **Environment variables** - Runtime environment settings  
3. **Configuration files** - YAML, TOML, or JSON files
4. **Default values** (lowest priority) - Built-in fallback values

---

1. **Create a configuration file**:
   ```bash
   python cli.py init-config --config-file flexvector.yaml
   ```

2. **Edit the configuration file** for your environment:
   ```yaml
   # flexvector.yaml
   environments:
     development:
       CHROMA_DB_FILE: "./data/vectorstores/chroma-dev"
       EMBEDDING_MODEL: "text-embedding-3-small"
     production:
       CHROMA_HTTP_URL: "https://prod-chroma.example.com"
       EMBEDDING_MODEL: "text-embedding-3-large"
   
   # Default settings
   EMBEDDING_DIMENSION: 512
   ```

3. **Use environment-specific settings**:
   ```bash
   # Development
   python cli.py load --input-dir ./docs --environment development
   
   # Production  
   python cli.py search --query "AI" --environment production
   ```

### .env File Support

```bash
cp env.example .env
# Edit .env with your local settings
```

📖 **[See full configuration documentation](docs/dynamic_configuration.md)** for advanced configuration patterns, multiple environments, and security best practices.


## Documentation

For more usage info, see [docs](./docs/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

*This package aims to be a versatile tool for various AI applications, including but not limited to:*

### Research and Development
- **Prototyping**: Quickly test different vector databases without changing your application code
- **A/B Testing**: Compare performance across different vector stores for your specific use case
- **Academic Research**: Study vector search behavior with a standardized interface


### RAG Pipeline Integration
Build robust Retrieval Augmented Generation (RAG) systems with a database-agnostic approach:
- **ETL Workflows**: Create efficient extract-transform-load pipelines that process documents and store embeddings without locking into a specific vector database
- **Multi-modal RAG**: Store and retrieve text, images, and other data types with the same consistent interface
- **Hybrid Search Systems**: Combine semantic search with traditional keyword search for improved retrieval quality

### Research and Development
- **Prototyping**: Quickly test different vector databases without changing your application code
- **A/B Testing**: Compare performance across different vector stores for your specific use case
- **Academic Research**: Study vector search behavior with a standardized interface

