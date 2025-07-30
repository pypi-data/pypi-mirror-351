# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .commitment_response import CommitmentResponse

__all__ = ["CommitmentSearchResponse"]


class CommitmentSearchResponse(BaseModel):
    data: Optional[List[CommitmentResponse]] = None
    """The list of Commitments information."""

    next_token: Optional[str] = FieldInfo(alias="nextToken", default=None)
    """The `nextToken` for multi-page retrievals.

    It is used to fetch the next page of Commitments in a paginated list.
    """
