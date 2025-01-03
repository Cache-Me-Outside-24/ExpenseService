from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel
from typing import List
from models.payment import Payment
from models.link import Link

router = APIRouter()

class GetPaymentsResponse(BaseModel):
    payments: List[Payment]
    links: List[Link]

@router.get(
    "/expenses/{expense_id}/payments",
    response_model=GetPaymentsResponse,
    status_code=200,
    summary="Get all of the payments for an expense",
    description="Retrieve detailed information about an expense's associated payments by its unique ID.",
    responses={
        200: {
            "description": "Request successful."
        },
        404: {"description": "Payments not found. No payments exist under the specified expense ID."},
    },
)
def get_payments(expense_id: str):
    sql = SQLMachine()

    payments_result = sql.select("expense_service_db", "payments", {"expense_id": expense_id})

    if not payments_result:
        raise HTTPException(status_code=404, detail="Payments not found.")
    
    payments = []

    for payment in payments_result:
        payments.append(Payment(expense_id=payment[0], payer_id=payment[1], amount_owed=payment[2], paid=payment[3]))

    # HATEOAS links
    links = [
            {"rel": "self", "href": f"/api/expenses/{expense_id}/payments"},
            {"rel": "expense", "href": f"/api/expenses/{expense_id}"}
        ]

    return GetPaymentsResponse(
        payments=payments,
        links=links
    )