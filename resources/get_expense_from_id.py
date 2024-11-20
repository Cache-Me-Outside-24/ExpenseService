from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel
from typing import List
from models.payment import Payment
from models.link import Link

router = APIRouter()

class GetExpenseResponse(BaseModel):
    expense_id: int
    total: float
    description: str
    group_id: int
    owed_to: str
    payments: List[Payment]
    links: List[Link]

@router.get(
    "/expenses/{expense_id}",
    response_model=GetExpenseResponse,
    status_code=200,
    summary="Get an expense by its Expense ID",
    description="Retrieve detailed information about an expense by its unique ID.",
    responses={
        200: {
            "description": "Request successful."
        },
        404: {"description": "Expense not found. The specified expense ID does not exist."},
    },
)
def get_expense(expense_id: str):
    sql = SQLMachine()

    result = sql.select("expense_service_db", "expenses", {"expense_id": int(expense_id)})

    # if no result found, raise a 404 error
    if not result:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    result = result[0]

    payments_result = sql.select("expense_service_db", "payments", {"expense_id": expense_id})
    payments = []

    for payment in payments_result:
        payments.append(Payment(expense_id=payment[0], payer_id=payment[1], amount_owed=payment[2], paid=payment[3]))

    # HATEOAS links
    links = [
            {"rel": "self", "href": f"/api/expenses/{expense_id}"},
            {"rel": "payments", "href": f"/api/expenses/{expense_id}/payments"}
        ]

    return GetExpenseResponse(
        expense_id=result[0],
        total=result[1],
        description=result[2],
        group_id=result[3],
        owed_to=result[4],
        payments=payments,
        links=links
    )