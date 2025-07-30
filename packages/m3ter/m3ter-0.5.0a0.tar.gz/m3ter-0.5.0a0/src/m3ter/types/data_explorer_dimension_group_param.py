# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DataExplorerDimensionGroupParam"]


class DataExplorerDimensionGroupParam(TypedDict, total=False):
    field_code: Required[Annotated[str, PropertyInfo(alias="fieldCode")]]
    """Field code to group by"""

    meter_id: Required[Annotated[str, PropertyInfo(alias="meterId")]]
    """Meter ID to group by"""

    group_type: Annotated[Literal["ACCOUNT", "DIMENSION", "TIME"], PropertyInfo(alias="groupType")]
