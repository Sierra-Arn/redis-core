# app/db/config.py
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class RedisConfig(BaseSettings):
    """
    Configuration schema for Redis service.

    Attributes
    ----------
    host : str
        Hostname or IP address of the Redis server. Default is `"127.0.0.1"`.
    internal_port : int
        TCP port the server listens on. Must be in the range 1-65535.
        Default is `6379`.
    username : str
        Username for Redis authentication.
    password : str
        Password for Redis authentication.
    db_index : int
        Redis database number to use for caching operations.
        Default is `0`.
    ttl_fast : int
        TTL in seconds for cached results of fast/cheap operations
        (e.g., API responses).
        Default is `300` (5 minutes).
    ttl_slow : int
        TTL in seconds for cached results of slow/expensive operations
        (e.g., loading ML models, running model inference).
        Default is `3600` (1 hours).

    Notes:
    ------
    1. Automatically loads settings from a `.env` file in the current working directory
       using a module-specific prefix specified.
    2. The `.env` file must use UTF-8 encoding. 
    3. Variable names are case-insensitive.
    4. Any extra (unrecognized) variables are silently ignored.
    5. The configuration is immutable after instantiation.
    6. During instantiation, values are resolved in the following order of precedence 
    (from highest to lowest priority):
        1. **Explicitly passed arguments** — values provided directly to the constructor.
        2. **Environment variables** — including those loaded from the `.env` file,
        prefixed according to the subclass's `env_prefix`.
        3. **Code-defined defaults** — fallback values specified as field defaults
        in the class definition.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        env_prefix="REDIS_"
    )

    host: str = "127.0.0.1"
    internal_port: int = Field(default=6379, ge=1, le=65535)
    username: str
    password: str
    db_index: int = Field(default=0)
    ttl_fast: int = Field(default=300, ge=0)
    ttl_slow: int = Field(default=3600, ge=0)

    @property
    def connection_url(self) -> str:
        """
        Build Redis connection URL from configuration settings.

        Returns
        -------
        str
            Complete Redis connection URL with URL-encoded credentials
            in the format: redis://username:password@host:port

        Notes
        -----
        The password is URL-encoded using `quote_plus` to safely handle
        special characters that might be present in the password string.
        """

        return (
            f"redis://{self.username}:"
            f"{quote_plus(self.password)}@"
            f"{self.host}:{self.internal_port}"
        )

# Initialize Redis configuration singleton
# Since Redis server settings are static for the application's lifetime
# and any configuration changes require a full application restart,
# it is safe to instantiate the config once at module level and reuse
# it throughout the application as a singleton.
redis_config = RedisConfig()