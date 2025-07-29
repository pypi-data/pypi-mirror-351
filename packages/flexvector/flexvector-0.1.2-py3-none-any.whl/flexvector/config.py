import json
from pathlib import Path
from typing import Any, Optional, Union

from loguru import logger
from pydantic import Field, SecretStr
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorDBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=False,
        case_sensitive=True,
        extra='ignore',
        env_file='.env',
    )

    # Chroma - https://docs.trychroma.com/docs/run-chroma/persistent-client
    CHROMA_DB_FILE: Optional[str] = "./data/vectorstores/chroma"
    CHROMA_HTTP_URL: Optional[str] = Field(None, description="URL of a remote Chroma DB server")
    CHROMA_HTTP_PORT: Optional[int] = Field(8000, description="Port of a remote Chroma DB server")
    CHROMA_API_KEY: Optional[str] = Field(None, description="API key for a remove Chroma DB server")

    # Qdrant - https://python-client.qdrant.tech/qdrant_client.qdrant_client
    QDRANT_HTTP_URL: Optional[str] = Field(None, description="URL of a remote QDrant server")
    QDRANT_API_KEY: Optional[str] = Field(None, description="API key for a remove QDrant server")
    QDRANT_LOCAL_PATH: Optional[str] = Field("./data/vectorstores/qdrant",
                                                description="Path to local QDrant server data directory")

    # Weaviate
    WEAVIATE_HTTP_URL: Optional[str] = Field(None, description="URL of a remote WEAVIATE server")
    WEAVIATE_API_KEY: Optional[str] = Field(None, description="API key for a remove WEAVIATE server")
    WEAVIATE_CLOUD_ENABLED: Optional[bool] = Field(None, description="Whether to use WEAVIATE cloud or custom server")

    # PG Vector Store - https://github.com/pgvector/pgvector
    PG_VECTOR_CONNECTION: Optional[str] = Field(None,
                                                description="URL of a remote PostgreSQL server with pg_vector extension")

    # Azure AI Search - https://pypi.org/project/azure-search-documents/
    AZURE_SEARCH_ENDPOINT: Optional[str] = Field(None, description="URL of a remote Azure Search endpoint")
    AZURE_SEARCH_ADMIN_KEY: Optional[str] = Field(None, description="Admin API key for Azure Search")
    AZURE_SEARCH_API_KEY: Optional[str] = Field(None, description="API key for Azure Search")

    EMBEDDING_DIMENSION: Optional[int] = Field(512, description="Embedding dimension")

    # Open AI
    OPENAI_API_KEY: Optional[SecretStr] = Field(None, description="API key for OpenAI")
    EMBEDDING_MODEL: Optional[str] = Field("text-embedding-3-small", description="Embedding model")

    # Open source embeddings
    SENTENCE_TRANSFORMER_MODEL: Optional[str] = Field(None, description="Sentence transformer embedding model")

    # Extras
    # https://docs.tavily.com/documentation/quickstart
    TAVILY_API_KEY: Optional[str] = Field(None,
                                          description="API key for Tavily API used for grounding LLM responses using web results")


class ConfigManager:
    """Configuration management for flexvector CLI.

    Supports multiple configuration sources with priority order:
    1. CLI arguments (highest priority)
    2. Environment variables
    3. Configuration files (YAML/TOML/JSON)
    4. Defaults (lowest priority)
    """

    def __init__(self) -> None:
        self.config_search_paths = [
            Path.cwd(),  # Current working directory
            Path.home() / ".flexvector",  # User config directory
            Path("/etc/flexvector"),  # System config directory
        ]

    def load_from_file(self, file_path: Union[str, Path]) -> dict[str, Any]:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            content = file_path.read_text(encoding='utf-8')

            if file_path.suffix.lower() in ['.yml', '.yaml']:
                return self._load_yaml(content)
            elif file_path.suffix.lower() == '.toml':
                return self._load_toml(content)
            elif file_path.suffix.lower() == '.json':
                return json.loads(content)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

        except Exception as e:
            raise ValueError(f"Failed to parse configuration file {file_path}: {e}")

    @staticmethod
    def _load_yaml(content: str) -> dict[str, Any]:
        try:
            import yaml
            return yaml.safe_load(content) or {}
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML configuration files. "
                "Install it with: pip install pyyaml"
            )

    @staticmethod
    def _load_toml(content: str) -> dict[str, Any]:
        try:
            import tomllib  # Python 3.11+
            return tomllib.loads(content)
        except ImportError:
            try:
                import toml
                return toml.loads(content)
            except ImportError:
                raise ImportError(
                    "tomllib (Python 3.11+) or toml library is required for TOML files. "
                    "For older Python versions, install with: pip install toml"
                )

    def find_config_file(self, filename: str) -> Optional[Path]:
        """Find configuration file in search paths."""
        for search_path in self.config_search_paths:
            config_file = search_path / filename
            if config_file.exists():
                logger.debug(f"Found config file: {config_file}")
                return config_file
        return None

    def auto_discover_config(self) -> Optional[dict[str, Any]]:
        """Auto-discover configuration files in standard locations."""
        config_filenames = [
            "flexvector.yaml",
            "flexvector.yml",
            "flexvector.toml",
            "flexvector.json",
            ".flexvector.yaml",
            ".flexvector.yml",
            ".flexvector.toml",
            ".flexvector.json",
        ]

        for filename in config_filenames:
            config_file = self.find_config_file(filename)
            if config_file:
                logger.info(f"Loading configuration from: {config_file}")
                return self.load_from_file(config_file)

        logger.debug("No configuration file found in standard locations")
        return None

    def load_settings(
            self,
            config_file: Optional[str] = None,
            cli_overrides: Optional[dict[str, Any]] = None,
            environment: Optional[str] = None
    ) -> VectorDBSettings:
        """
        Load settings from multiple sources with priority order.

        Args:
            config_file: Specific configuration file path
            cli_overrides: Dictionary of CLI argument overrides
            environment: Environment name (dev, staging, prod)

        Returns:
            VectorDBSettings instance with merged configuration
        """
        config_data = {}

        # 1. Load from configuration file (lowest priority)
        if config_file:
            try:
                file_config = self.load_from_file(config_file)
                config_data.update(file_config)
                logger.info(f"Loaded configuration from: {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
        else:
            # Auto-discover configuration
            auto_config = self.auto_discover_config()
            if auto_config:
                config_data.update(auto_config)

        # 2. Apply environment-specific overrides
        if environment:
            env_config = config_data.get('environments', {}).get(environment, {})
            config_data.update(env_config)
            logger.info(f"Applied environment-specific config: {environment}")

        # 3. Create settings (will load from env vars and .env files)
        try:
            # Filter out non-field keys like 'environments'
            filtered_config = {
                k: v for k, v in config_data.items()
                if k.upper() in VectorDBSettings.model_fields or not k.islower()
            }

            settings_instance = VectorDBSettings(**filtered_config)
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            logger.debug("Falling back to default settings")
            # noinspection PyArgumentList
            settings_instance = VectorDBSettings()

        # 4. Apply CLI overrides (highest priority)
        if cli_overrides:
            for key, value in cli_overrides.items():
                if value is not None:
                    field_name = key.upper()
                    if hasattr(settings_instance, field_name):
                        setattr(settings_instance, field_name, value)
                        logger.debug(f"CLI override: {field_name} = {value}")

        return settings_instance

    def create_sample_config(self, file_path: Union[str, Path], format_: str = "yaml") -> None:
        """Create a sample configuration file."""
        file_path = Path(file_path)

        sample_config = {
            "# FlexVector Configuration": "Sample configuration file",
            "environments": {
                "development": {
                    "CHROMA_DB_FILE": "./data/vectorstores/chroma-dev",
                    "QDRANT_LOCAL_PATH": "./data/vectorstores/qdrant-dev"
                },
                "staging": {
                    "CHROMA_HTTP_URL": "http://staging-chroma:8000",
                    "QDRANT_HTTP_URL": "http://staging-qdrant:6333"
                },
                "production": {
                    "CHROMA_HTTP_URL": "https://prod-chroma.example.com",
                    "QDRANT_HTTP_URL": "https://prod-qdrant.example.com"
                }
            },
            "EMBEDDING_DIMENSION": 512,
            "EMBEDDING_MODEL": "text-embedding-3-small"
        }

        if format_.lower() == "yaml":
            content = self._dict_to_yaml(sample_config)
        elif format_.lower() == "toml":
            content = self._dict_to_toml(sample_config)
        elif format_.lower() == "json":
            content = json.dumps(sample_config, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_}")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"Created sample configuration file: {file_path}")

    @staticmethod
    def _dict_to_yaml(data: dict[str, Any]) -> str:
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except ImportError:
            raise ImportError("PyYAML is required to create YAML config files")

    @staticmethod
    def _dict_to_toml(data: dict[str, Any]) -> str:
        try:
            import toml
            return toml.dumps(data)
        except ImportError:
            raise ImportError("toml library is required to create TOML config files")


# noinspection PyArgumentList
settings = VectorDBSettings()
config_manager = ConfigManager()
