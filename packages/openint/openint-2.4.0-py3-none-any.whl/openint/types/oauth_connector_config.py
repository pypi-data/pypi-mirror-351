# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["OAuthConnectorConfig"]


class OAuthConnectorConfig(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None
