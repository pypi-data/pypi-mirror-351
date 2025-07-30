"""
Application settings using Pydantic for environment variable management.

Provides type-safe, validated configuration with defaults and environment 
variable override support.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

try:
    from pydantic import Field, validator
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings, Field, validator
from typing import Annotated


class RedisSettings(BaseSettings):
    """Redis connection and performance settings."""

    REDIS_HOST: str = Field(default="localhost", description="Redis server host")
    REDIS_PORT: int = Field(default=6379, description="Redis server port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_UNIX_SOCKET_PATH: Optional[str] = Field(
        default=None, description="Redis Unix domain socket path (e.g., '/var/run/redis/redis.sock') - saves 80-120µs per operation"
    )
    REDIS_POOL_SIZE: Annotated[int, Field(gt=4, lt=512)] = Field(
        default=16, description="Redis connection pool size (CPU cores * 2)"
    )
    REDIS_SOCKET_TIMEOUT: float = Field(
        default=0.050, description="Redis socket timeout (50ms)"
    )
    REDIS_SOCKET_CONNECT_TIMEOUT: float = Field(
        default=0.050, description="Redis connect timeout (50ms)"
    )
    REDIS_SOCKET_KEEPALIVE: bool = Field(
        default=True, description="Enable TCP keepalive"
    )
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(
        default=30, description="Health check interval"
    )

    class Config:
        env_prefix = "SENTR_"
        case_sensitive = True


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    NEO4J_URI: str = Field(
        default="bolt://localhost:7687", description="Neo4j connection URI"
    )
    NEO4J_USER: str = Field(default="neo4j", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(default="password", description="Neo4j password")
    NEO4J_DATABASE: str = Field(default="neo4j", description="Neo4j database name")
    NEO4J_MAX_CONNECTION_LIFETIME: int = Field(
        default=3600, description="Neo4j max connection lifetime"
    )
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(
        default=50, description="Neo4j connection pool size"
    )
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: float = Field(
        default=60.0, description="Neo4j connection timeout"
    )

    class Config:
        env_prefix = ""
        case_sensitive = True


class PerformanceSettings(BaseSettings):
    """Performance and optimization settings."""

    FEATURE_BATCH_SIZE: int = Field(
        default=1000, description="Feature processing batch size"
    )
    JSON_BACKEND: str = Field(
        default="orjson", description="JSON backend (orjson or stdlib)"
    )
    STRING_INTERNING_ENABLED: bool = Field(
        default=True, description="Enable string interning"
    )
    REDIS_PIPELINE_SIZE: int = Field(
        default=100, description="Redis pipeline batch size"
    )
    SLIDING_WINDOW_MAX_SIZE: int = Field(
        default=10000, description="Sliding window max events"
    )
    MEMORY_THRESHOLD_MB: int = Field(default=1024, description="Memory usage threshold")

    @validator("JSON_BACKEND")
    def validate_json_backend(cls, v):
        if v not in ["orjson", "stdlib"]:
            raise ValueError('JSON_BACKEND must be "orjson" or "stdlib"')
        return v

    class Config:
        env_prefix = ""
        case_sensitive = True


class ModelSettings(BaseSettings):
    """Machine learning model settings."""

    MODEL_PATH: str = Field(default="/app/models", description="Model storage path")
    TGAT_MODEL_PATH: Optional[str] = Field(
        default=None, description="TGAT model file path"
    )
    MODEL_CACHE_SIZE: int = Field(default=100, description="Model cache size")
    MODEL_INFERENCE_TIMEOUT: float = Field(
        default=5.0, description="Model inference timeout"
    )
    BATCH_INFERENCE_SIZE: int = Field(default=32, description="Batch inference size")

    class Config:
        env_prefix = ""
        case_sensitive = True


class APISettings(BaseSettings):
    """API server settings."""

    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")
    API_WORKERS: int = Field(default=1, description="Number of API workers")
    API_LOG_LEVEL: str = Field(default="info", description="API log level")
    API_TIMEOUT: float = Field(default=30.0, description="API request timeout")
    API_MAX_REQUEST_SIZE: int = Field(
        default=16 * 1024 * 1024, description="Max request size"
    )
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS allowed origins")

    @validator("API_LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in valid_levels:
            raise ValueError(f"API_LOG_LEVEL must be one of {valid_levels}")
        return v.lower()

    class Config:
        env_prefix = ""
        case_sensitive = True


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""

    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics server port")
    METRICS_PATH: str = Field(default="/metrics", description="Metrics endpoint path")
    HEALTH_CHECK_ENABLED: bool = Field(default=True, description="Enable health checks")
    HEALTH_CHECK_PATH: str = Field(
        default="/health", description="Health check endpoint"
    )
    LOG_LEVEL: str = Field(default="INFO", description="Application log level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @validator("LOG_FORMAT")
    def validate_log_format(cls, v):
        if v.lower() not in ["json", "text"]:
            raise ValueError('LOG_FORMAT must be "json" or "text"')
        return v.lower()

    class Config:
        env_prefix = ""
        case_sensitive = True


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""

    SECRET_KEY: str = Field(
        default="dev-secret-key", description="Application secret key"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration"
    )
    PASSWORD_HASH_ALGORITHM: str = Field(
        default="bcrypt", description="Password hashing algorithm"
    )
    API_KEY_HEADER: str = Field(default="X-API-Key", description="API key header name")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="Rate limit per minute")

    class Config:
        env_prefix = ""
        case_sensitive = True


class SentrSettings(
    RedisSettings,
    DatabaseSettings,
    PerformanceSettings,
    ModelSettings,
    APISettings,
    MonitoringSettings,
    SecuritySettings,
):
    """Main Sentr application settings combining all setting groups."""

    # Application metadata
    APP_NAME: str = Field(default="Sentr", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(
        default="development", description="Environment (dev/staging/prod)"
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Feature flags
    GRAPH_SCORING_ENABLED: bool = Field(
        default=True, description="Enable graph-based scoring"
    )
    RULES_ENGINE_ENABLED: bool = Field(default=True, description="Enable rules engine")
    FEATURE_STORE_ENABLED: bool = Field(
        default=True, description="Enable feature store"
    )

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v.lower()

    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_neo4j_config(self) -> Dict[str, Any]:
        """Get Neo4j configuration dictionary."""
        return {
            "uri": self.NEO4J_URI,
            "auth": (self.NEO4J_USER, self.NEO4J_PASSWORD),
            "database": self.NEO4J_DATABASE,
            "max_connection_lifetime": self.NEO4J_MAX_CONNECTION_LIFETIME,
            "max_connection_pool_size": self.NEO4J_MAX_CONNECTION_POOL_SIZE,
            "connection_acquisition_timeout": self.NEO4J_CONNECTION_ACQUISITION_TIMEOUT,
        }

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def as_dict(self) -> Dict[str, Any]:
        """Return settings as dictionary for logging/metrics export."""
        return dict(self)

    def reload(self) -> None:
        """Reload settings from environment (can be triggered by SIGHUP)."""
        self.__dict__.clear()
        self.__init__()
        self.model_rebuild()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        env_prefix = "SENTR_"


@lru_cache
def get_settings() -> SentrSettings:
    """
    Get cached application settings.

    Returns:
        SentrSettings instance (cached for performance)
    """
    return SentrSettings()


# One true instance - all imports share this to avoid re-parsing env vars
settings = SentrSettings()


# Environment-specific setting overrides
def get_development_settings() -> SentrSettings:
    """Get settings optimized for development."""
    settings = get_settings()
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.REDIS_POOL_SIZE = 5  # Smaller pool for dev
    return settings


def get_production_settings() -> SentrSettings:
    """Get settings optimized for production."""
    settings = get_settings()
    settings.DEBUG = False
    settings.LOG_LEVEL = "INFO"
    settings.LOG_FORMAT = "json"
    settings.REDIS_POOL_SIZE = 50  # Larger pool for production
    return settings


def load_settings_from_env() -> SentrSettings:
    """
    Load settings from environment variables.

    Returns:
        SentrSettings instance with environment overrides
    """
    # Clear cache to force reload
    get_settings.cache_clear()
    return get_settings()
