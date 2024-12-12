from fastapi import APIRouter, HTTPException, Response
from services.sql_comands import SQLMachine
from models.create_expense_request import CreateExpenseRequest
from models.create_user_expense_split import CreateUserExpenseSplit
from models.link import Link
from pydantic import BaseModel
from typing import List

router = APIRouter()


class CreateExpenseResponse(BaseModel):
    expense_id: int
    split_ids: List[int]
    links: List[Link]


@router.post(
    "/expenses",
    status_code=201,
    summary="Create a new expense",
    description="Creates a new expense with a description, total amount, and amounts owed per person. Returns 201 Created with a link header if successful.",
    responses={
        201: {
            "description": "Group created successfully with Link header.",
            "headers": {
                "Link": {
                    "description": "URL of the created resource",
                    "schema": {"type": "string"},
                    "example": '</expenses/1>; rel="\created-resource"',
                }
            },
        },
        400: {"description": "Bad Request - Could not create the expense"},
    },
)
def create_new_expense(
    expense: CreateExpenseRequest,
    splits: List[CreateUserExpenseSplit],
    response: Response,
):
    try:
        sql = SQLMachine()

        expense_data = expense.model_dump()

        # format request data as expected by SQLMachine
        expenses_insert = {
            "total": expense_data["total"],
            "description": expense_data["description"],
            "group_id": expense_data["group_id"],
        }

        # insert expense data into db
        id = sql.insert("expense_service_db", "expenses", expenses_insert)

        split_ids = []
        for split in splits:
            split_data = split.model_dump()
            expense_split_insert = {
                "Expense ID": id,
                "Group ID": split_data["group_id"],
                "Payer ID": split_data["payer_id"],
                "Amount": split_data["amount"],
                "Timestamp": split_data["timestamp"],
                "Payee ID": split_data["payee_id"],
                "Payer Confirm": split_data["payer_confirm"],
                "Payee Confirm": split_data["payee_confirm"],
                "Label": split_data["label"],
            }

            split_id = sql.insert("expense_service_db", "expense", expense_split_insert)
            split_ids.append(split_id)

        # insert each payment into db
        for payment in expense_data["payments"]:
            payments_insert = {
                "expense_id": id,
                "payer_id": payment["payer_id"],
                "amount_owed": payment["amount_owed"],
                "paid": payment["paid"],
            }

            sql.insert("expense_service_db", "payments", payments_insert)

        # HATEOAS links
        links = [
            {"rel": "self", "href": f"/api/expenses/{id}"},
            {"rel": "payments", "href": f"/api/expenses/{id}/payments"},
        ]

        response.headers["Link"] = f'</groups/{id}>; rel="created_resource"'
        return CreateExpenseResponse(expense_id=id, split_ids=split_ids, links=links)
    except Exception as e:
        print(repr(e))
        raise HTTPException(
            status_code=400, detail="An error occurred while creating the expense"
        )
