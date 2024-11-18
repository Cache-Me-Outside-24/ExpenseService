from pydantic import BaseModel
from typing import List, Optional

class Payment(BaseModel):
    expense_id: Optional[int]
    payer_id: str
    amount_owed: float
    paid: bool

class CreateExpenseRequest(BaseModel):
    total: float
    description: str
    group_id: int
    owed_to: str
    payments: List[Payment]