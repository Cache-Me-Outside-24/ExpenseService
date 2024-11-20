from fastapi import APIRouter, HTTPException, Response
from services.sql_comands import SQLMachine

router = APIRouter()

@router.delete(
    "/expenses/{expense_id}/payments/{payer_id}",
    status_code=204,
    summary="Delete a payment",
    description="Delete the payment with the corresponding payer and expense IDs.",
    responses={
        404: {"description": "Payment not found. The specified resource does not exist."},
        500: {"description": "Something strange happened."}
    },
)
def delete_payment(
    expense_id: str, payer_id: str
):
    sql = SQLMachine()

    result = sql.delete("expense_service_db", "payments", {"expense_id": expense_id, "payer_id": payer_id})

    if result == 0:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if result > 1:
        raise HTTPException(status_code=500, detail=f"Too many ({result}) rows deleted.")
    
    return Response(status_code=204)