# nextpertise-envy-settings

A reusable Pydantic `BaseSettings` subclass that fetches environment variables from an Envy API using a Keycloak-secured token. It automatically writes these variables to a `.env.envy` file and prepends it to your environment configuration.

---

## ✨ Features

- ✅ Compatible with **Pydantic v1**
- 🔐 Uses **OAuth2 client credentials** flow via Keycloak
- 📄 Automatically fetches and stores `.env.envy`
- 🧠 Prepend `.env.envy` to Pydantic's `env_file` list
- 🛡 Graceful fallback to existing file if API fails

---

## 📦 Installation

```bash
poetry add nextpertise-envy-settings

Or with pip:

pip install nextpertise-envy-settings


⸻

🚀 Usage

from envy_settings import EnvySettings

class Settings(EnvySettings):
    mysql_user: str

    class Config(EnvySettings.Config):
        envy_url = "https://myenvy.com"
        envy_keycloak_url = "https://mykeycloak.com/realms/realm"
        envy_keycloak_client_id = "your-clientid"
        envy_keycloak_token = "your-client-secret"
        envy_environment = "your-environment"
        env_file = (".env",)


⸻

🔧 Environment Variables (optional)

Instead of hardcoding the config, you can also use these environment variables:

Variable	Description
ENV_API_BASE_URL	Base URL for Envy API
ENV_API_KEYCLOAK_URL	Keycloak realm URL
ENV_API_KEYCLOAK_CLIENT_ID	OAuth2 client ID
ENV_API_KEYCLOAK_TOKEN	OAuth2 client secret
ENV_API_ENVIRONMENT	Target environment name


⸻

📁 Example .env.envy

MYSQL_USER=abc
MYSQL_PASSWORD=xyz
REDIS_HOST=localhost
