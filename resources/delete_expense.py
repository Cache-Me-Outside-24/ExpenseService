from fastapi import APIRouter, HTTPException, Response
from services.sql_comands import SQLMachine

router = APIRouter()

@router.delete(
    "/expenses/{expense_id}",
    status_code=204,
    summary="Delete an expense",
    description="Delete the expense with the corresponding expense ID, along with any associated payments.",
    responses={
        404: {"description": "Expense not found. The specified expense ID does not exist."},
        500: {"description": "Something strange happened."}
    },
)
def delete_expense(
    expense_id: str
):
    sql = SQLMachine()

    result = sql.delete("expense_service_db", "payments", {"expense_id": expense_id})
    result = sql.delete("expense_service_db", "expenses", {"expense_id": expense_id})

    if result == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if result > 1:
        raise HTTPException(status_code=500, detail=f"Too many ({result}) rows deleted.")
    
    return Response(status_code=204)