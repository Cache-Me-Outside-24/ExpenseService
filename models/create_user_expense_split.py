from pydantic import BaseModel
from datetime import datetime


class CreateUserExpenseSplit(BaseModel):
    group_id: int
    payer_id: str
    amount: float
    timestamp: datetime
    payee_id: str
    payer_confirm: bool
    payee_confirm: bool
    label: str
