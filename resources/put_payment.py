from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel, Field
from typing import List, Optional
from models.payment import Payment
from models.link import Link

router = APIRouter()

class PutPaymentResponse(BaseModel):
    payment: Payment
    links: List[Link]

class PutPaymentRequest(BaseModel):
    amount_owed: Optional[float] = Field(None)
    paid: Optional[bool] = Field(None)

@router.put(
    "/expenses/{expense_id}/payments/{payer_id}",
    response_model=PutPaymentResponse,
    status_code=200,
    summary="Add or modify a payment for an expense",
    description="Modifies the payment corresponding to the expense and payer specified in the URL. If the payment does not already exist, it will be created.",
    responses={
        200: {
            "description": "Request successful."
        },
        404: {"description": "Expense not found. There is no expense for the specified expense ID."},
    },
)
def put_payment(request: PutPaymentRequest, expense_id: str, payer_id: str):
    sql = SQLMachine()

    payment_result = sql.select("expense_service_db", "payments", {"expense_id": expense_id, "payer_id": payer_id})

    request = request.model_dump(exclude_unset=True)

    # HATEOAS links
    links = [
            {"rel": "self", "href": f"/api/expenses/{expense_id}/payments/{payer_id}"},
            {"rel": "payments", "href": f"/api/expenses/{expense_id}/payments"},
            {"rel": "expense", "href": f"/api/expenses/{expense_id}"}
        ]

    if not payment_result: # the payment doesnt exist -> check for expense
        expense_result = sql.select("expense_service_db", "expenses", {"expense_id": expense_id})

        # If the expense doesn't exist throw a 404 error
        if not expense_result:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Otherwise, insert a new payment

        # Make sure all fields are present before inserting
        if "amount_owed" not in request or "paid" not in request:
            raise HTTPException(status_code=400, detail="Both 'amound_owed' and 'paid' are required for resource creation.")

        payments_insert = {
                "expense_id": expense_id,
                "payer_id": payer_id,
                "amount_owed": request["amount_owed"],
                "paid": request["paid"]
            }

        sql.insert("expense_service_db", "payments", payments_insert)

        return PutPaymentResponse(
            payment=payments_insert,
            links=links
        )
    else:
        payment_result = payment_result[0]

        result = sql.update("expense_service_db", "payments", {"expense_id": expense_id, "payer_id": payer_id}, request)

        # TODO: return different code if no change has been made?
        if result < 2:
            payment = Payment(
                expense_id=expense_id,
                payer_id=payer_id,
                amount_owed=payment_result[2] if "amount_owed" not in request else request["amount_owed"],
                paid=payment_result[3] if "paid" not in request else request["paid"])
                        
            return PutPaymentResponse(
                payment=payment,
                links=links
            )
