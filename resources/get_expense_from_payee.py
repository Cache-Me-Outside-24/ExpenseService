from fastapi import APIRouter, HTTPException
from services.sql_comands import SQLMachine
from pydantic import BaseModel
from typing import List
from models.link import Link

router = APIRouter()


class GetUserExpenseResponse(BaseModel):
    expense_id: int
    amount: float
    description: str
    group_id: int
    group_name: str
    links: List[Link]


@router.get(
    "/expenses/payee/{user_id}",
    response_model=List[GetUserExpenseResponse],
    status_code=200,
    summary="Get all expenses associated with user ID",
    description="Retrieve information about the expenses of user by user ID.",
    responses={
        200: {"description": "Request successful."},
        404: {
            "description": "Expenses not found. The specified user ID does not exist."
        },
    },
)
def get_user_expenses(user_id: str):
    sql = SQLMachine()

    try:
        # Fetch expenses where the user is the payer
        expenses = sql.select(
            schema="expense_service_db",
            table="expense",
            data={"payee_id": user_id},
        )

        if not expenses:
            raise HTTPException(
                status_code=404, detail="No expenses found for this user."
            )

        expense_responses = []

        for expense in expenses:
            expense_id = expense[0]  # Expense ID
            group_id = expense[1]  # Group ID
            amount = expense[3]  # Amount
            description = expense[4]  # Description

            # Fetch group name using group_id
            group = sql.select(
                schema="group_service_db",
                table="groups",
                data={"group_id": group_id},
            )

            if not group:
                group_name = "Unknown Group"
            else:
                group_name = group[0][1]  # Assuming group_name is the second column

            # Create HATEOAS links
            links = [
                Link(rel="self", href=f"/expenses/{expense_id}"),
                Link(rel="group", href=f"/groups/{group_id}"),
            ]

            # Build response object
            expense_responses.append(
                GetUserExpenseResponse(
                    expense_id=expense_id,
                    amount=amount,
                    description=description,
                    group_id=group_id,
                    group_name=group_name,
                    links=links,
                )
            )

        return expense_responses

    except Exception as e:
        print(f"Error fetching expenses for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching expenses."
        )
