# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["GetCurrentUserResponse"]


class GetCurrentUserResponse(BaseModel):
    role: Literal["anon", "customer", "user", "org", "system"]

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
