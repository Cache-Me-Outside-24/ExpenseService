from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel, Field
from typing import List, Optional
from models.payment import Payment
from models.link import Link

router = APIRouter()


class ConfirmPaymentRequest(BaseModel):
    payer_id: str


@router.put(
    "/expenses/{expense_id}/confirm/{payee_id}",
    status_code=200,
    summary="Confrim a payment for an expense",
    description="Modifies the payment corresponding to the expense and payer specified in the URL. If the payment does not already exist, it will be created.",
    responses={
        200: {"description": "Request successful."},
        404: {
            "description": "Expense not found. There is no expense for the specified expense ID."
        },
    },
)
def confirm_payment(request: ConfirmPaymentRequest, expense_id: str, payee_id: str):
    sql = SQLMachine()
    payer_id = request.payer_id

    expense_result = sql.update(
        "expense_service_db",
        "expense",
        {"`Expense ID`": expense_id, "`Payer ID`": payer_id, "`Payee ID`": payee_id},
        {"`Payee Confirm`": True},
    )
    payment_result = sql.update(
        "expense_service_db",
        "payments",
        {"expense_id": expense_id, "payer_id": payer_id},
        {"paid": True},
    )
