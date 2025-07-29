from pydantic import BaseSettings
import requests
import os
class EnvFetchError(Exception):
    pass

class EnvySettings(BaseSettings):
    class Config:
        # Configurable in subclasses or via env vars
        envy_url: str = None
        envy_keycloak_url: str = None
        envy_keycloak_client_id: str = None
        envy_keycloak_token: str = None  # client secret
        envy_environment: str = None
        envy_filename: str = ".env.envy"
        env_file = (".env",)
        env_file_encoding: str = "utf-8"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cfg = cls.Config
        envy_url = (getattr(cfg, "envy_url", None) or os.getenv("ENV_API_BASE_URL", "")).rstrip("/")
        keycloak_url = (getattr(cfg, "envy_keycloak_url", None) or os.getenv("ENV_API_KEYCLOAK_URL", "")).rstrip("/")
        client_id = getattr(cfg, "envy_keycloak_client_id", None) or os.getenv("ENV_API_KEYCLOAK_CLIENT_ID")
        client_secret = getattr(cfg, "envy_keycloak_token", None) or os.getenv("ENV_API_KEYCLOAK_TOKEN")
        envy_env = getattr(cfg, "envy_environment", None) or os.getenv("ENV_API_ENVIRONMENT")
        envy_filename = getattr(cfg, "envy_filename", ".env.envy")
        env_file_encoding = getattr(cfg, "env_file_encoding", "utf-8")

        if not all([envy_url, keycloak_url, client_id, client_secret, envy_env]):
            return

        env_file_path = Path(envy_filename)

        try:
            # Step 1: Exchange client credentials for access token
            token_url = f"{keycloak_url}/protocol/openid-connect/token"
            token_response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                }
            )

            if token_response.status_code != 200:
                raise EnvFetchError(f"Token exchange failed: {token_response.status_code}")

            access_token = token_response.json().get("access_token")
            if not access_token:
                raise EnvFetchError("Token exchange succeeded but no access_token returned.")

            # Step 2: Fetch .env from API
            response = requests.get(
                f"{envy_url}/environments/{envy_env}/variables",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "text/plain",
                },
            )

            if response.status_code != 200:
                raise EnvFetchError(f"Failed to fetch env: {response.status_code}")

            env_file_path.write_text(response.text, encoding=env_file_encoding)

        except (requests.RequestException, EnvFetchError) as e:
            if env_file_path.exists():
                print(f"[envy] Warning: {e}. Using existing {env_file_path}.")
                return
            raise EnvFetchError(f"Cannot proceed: {e}")

        # Prepend envy file to env_file list
        original = getattr(cfg, "env_file", ())
        if isinstance(original, str):
            original = (original,)
        cls.Config.env_file = (envy_filename,) + tuple(original)
