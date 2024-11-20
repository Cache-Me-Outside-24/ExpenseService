from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel
from typing import List
from models.payment import Payment
from models.link import Link

router = APIRouter()

class GetPaymentResponse(BaseModel):
    payment: Payment
    links: List[Link]

@router.get(
    "/expenses/{expense_id}/payments/{payer_id}",
    response_model=GetPaymentResponse,
    status_code=200,
    summary="Get a payment for an expense",
    description="Retrieve detailed information about a payment associated with a specific expense.",
    responses={
        200: {
            "description": "Request successful."
        },
        404: {"description": "Payment not found. There is no payment for the specified user under this expense."},
    },
)
def get_payment(expense_id: str, payer_id: str):
    sql = SQLMachine()

    payment_result = sql.select("expense_service_db", "payments", {"expense_id": expense_id, "payer_id": payer_id})

    if not payment_result:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_result = payment_result[0]

    payment = Payment(expense_id=payment_result[0], payer_id=payment_result[1], amount_owed=payment_result[2], paid=payment_result[3])

    # HATEOAS links
    links = [
            {"rel": "self", "href": f"/api/expenses/{expense_id}/payments/{payer_id}"},
            {"rel": "payments", "href": f"/api/expenses/{expense_id}/payments"},
            {"rel": "expense", "href": f"/api/expenses/{expense_id}"}
        ]

    return GetPaymentResponse(
        payment=payment,
        links=links
    )