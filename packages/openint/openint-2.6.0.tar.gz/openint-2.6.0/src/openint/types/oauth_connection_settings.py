# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["OAuthConnectionSettings", "Credentials"]


class Credentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class OAuthConnectionSettings(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[Credentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None
