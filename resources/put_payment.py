from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel, Field
from typing import List, Optional
from models.payment import Payment
from models.link import Link

router = APIRouter()


class PaymentPut(BaseModel):
    expense_id: Optional[int] = Field(None)
    payer_id: str
    amount_owed: float
    paid: bool
    method: str
    group_id: int
    payee_id: str


class PutPaymentResponse(BaseModel):
    payment: PaymentPut
    links: List[Link]


class PutPaymentRequest(BaseModel):
    amount_owed: float
    group_id: int
    method: str
    payee_id: str


@router.put(
    "/expenses/{expense_id}/payments/{payer_id}",
    response_model=PutPaymentResponse,
    status_code=200,
    summary="Add or modify a payment for an expense",
    description="Modifies the payment corresponding to the expense and payer specified in the URL. If the payment does not already exist, it will be created.",
    responses={
        200: {"description": "Request successful."},
        404: {
            "description": "Expense not found. There is no expense for the specified expense ID."
        },
    },
)
def put_payment(request: PutPaymentRequest, expense_id: str, payer_id: str):
    sql = SQLMachine()

    amount = request.amount_owed
    group_id = request.group_id
    method = request.method
    payee_id = request.payee_id

    expense_result = sql.update(
        "expense_service_db",
        "expense",
        {"`Expense ID`": expense_id, "`Payer ID`": payer_id, "`Payee ID`": payee_id},
        {"`Payer Confirm`": True},
    )

    payments_insert = {
        "expense_id": expense_id,
        "payer_id": payer_id,
        "amount_owed": amount,
        "paid": False,
        "method": method,
        "group_id": group_id,
        "payee_id": payee_id,
    }
    # HATEOAS links
    links = [
        {"rel": "self", "href": f"/api/expenses/{expense_id}/payments/{payer_id}"},
        {"rel": "payments", "href": f"/api/expenses/{expense_id}/payments"},
        {"rel": "expense", "href": f"/api/expenses/{expense_id}"},
    ]

    sql.insert("expense_service_db", "payments", payments_insert)

    return PutPaymentResponse(payment=payments_insert, links=links)
