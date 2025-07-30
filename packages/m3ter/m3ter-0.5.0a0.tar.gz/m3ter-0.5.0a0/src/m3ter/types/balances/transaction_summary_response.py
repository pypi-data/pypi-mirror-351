# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TransactionSummaryResponse"]


class TransactionSummaryResponse(BaseModel):
    initial_credit_amount: Optional[float] = FieldInfo(alias="initialCreditAmount", default=None)

    total_credit_amount: Optional[float] = FieldInfo(alias="totalCreditAmount", default=None)

    total_debit_amount: Optional[float] = FieldInfo(alias="totalDebitAmount", default=None)
