from pydantic import BaseModel
from typing import List
from models.payment import Payment

class CreateExpenseRequest(BaseModel):
    total: float
    description: str
    group_id: int
    owed_to: str
    payments: List[Payment]