"""Base settings for MCP and Gateway."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KeycloakSettings(BaseSettings):
    """Settings for Keycloak."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="KEYCLOAK_", env_file=".env", extra="allow"
    )

    server_url: str
    realm: str
    client_id: str
    client_secret: str
    redirect_uri: str
    algorithm: str = "RS256"


keycloak_settings = KeycloakSettings()


class AuthDefaultSettings(BaseSettings):
    """Settings for Basic Auth."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="AUTH_", env_file=".env", extra="allow"
    )

    # The name of the auth service
    service_name: str = "auth_service"

    # The api endpoint of the application which is used to redirect to the login page
    application_endpoint: str

    # The secret key for the encryption
    basic_auth_encryption_key: str = (
        "425df05bf30c8434e8a619563b602a7aa0421011f71727289eee66d310897118"
    )

    # The collection name for the basic auth user
    basic_auth_user_collection: str = "basic_auth_user"

    # The http client ssl verify
    http_client_ssl_verify: bool = True

    # The http client timeout
    http_client_timeout: int = 30


auth_default_settings = AuthDefaultSettings()
