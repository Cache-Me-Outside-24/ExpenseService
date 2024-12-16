from pydantic import BaseModel, Field
from typing import Optional


class Payment(BaseModel):
    expense_id: Optional[int] = Field(None)
    payer_id: str
    amount_owed: float
    paid: bool
    method: str
    group_id: str
