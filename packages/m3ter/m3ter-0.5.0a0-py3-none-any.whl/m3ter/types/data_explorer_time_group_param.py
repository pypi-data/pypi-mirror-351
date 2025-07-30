# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DataExplorerTimeGroupParam"]


class DataExplorerTimeGroupParam(TypedDict, total=False):
    frequency: Required[Literal["DAY", "HOUR", "WEEK", "MONTH", "QUARTER"]]
    """Frequency of usage data"""

    group_type: Annotated[Literal["ACCOUNT", "DIMENSION", "TIME"], PropertyInfo(alias="groupType")]
