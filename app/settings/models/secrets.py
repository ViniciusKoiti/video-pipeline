from __future__ import annotations

from pydantic import SecretStr

from app.settings.models._settings_model import _Model


class Secrets(_Model):
    pexels_api_key: SecretStr | None = None
    pixabay_api_key: SecretStr | None = None
    unsplash_access_key: SecretStr | None = None
    cloudflare_account_id: SecretStr | None = None
    cloudflare_api_token: SecretStr | None = None
    groq_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    postiz_api_key: SecretStr | None = None
