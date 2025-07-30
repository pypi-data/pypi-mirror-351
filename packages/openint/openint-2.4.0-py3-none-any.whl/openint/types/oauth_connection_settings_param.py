# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["OAuthConnectionSettingsParam", "Credentials"]


class Credentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class OAuthConnectionSettingsParam(TypedDict, total=False):
    created_at: str

    credentials: Credentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str
