from fastapi import APIRouter, HTTPException, Response
from services.sql_comands import SQLMachine
from models.create_expense_request import CreateExpenseRequest
from models.create_user_expense_split import CreateUserExpenseSplit
from models.link import Link
from pydantic import BaseModel
from typing import List
from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
topic_path = "projects/cache-me-outside-437317/topics/create-expense-group"

router = APIRouter()


class CreateExpenseResponse(BaseModel):
    expense_id: int
    split_ids: List[int]
    links: List[Link]


@router.post(
    "/expenses/create_expense_and_group",
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
def create_new_expense_and_group(
    expense: CreateExpenseRequest,
    splits: List[CreateUserExpenseSplit],
    response: Response,
):
    try:
        sql = SQLMachine()

        # Your existing expense creation logic
        expense_data = expense.model_dump()

        # Insert expense
        expenses_insert = {
            "total": expense_data["total"],
            "description": expense_data["description"],
            "group_id": expense_data["group_id"],
            "owed_to": expense_data["owed_to"],
        }

        id = sql.insert("expense_service_db", "expenses", expenses_insert)

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

            sql.insert("expense_service_db", "expense", expense_split_insert)

        # commented out for now since payments isnt being implemented
        """
        # Insert payments
        for payment in expense_data["payments"]:
            payments_insert = {
                "expense_id": id,
                "payer_id": payment["payer_id"],
                "amount_owed": payment["amount_owed"],
                "paid": payment["paid"],
            }
            sql.insert("expense_service_db", "payments", payments_insert)
        """

        # Publish to Pub/Sub
        publisher = pubsub_v1.PublisherClient()
        topic_path = "projects/cache-me-outside-437317/topics/create-expense-group"

        # Prepare message data
        message_data = json.dumps(
            {
                "expense_id": id,
                "total": expense_data["total"],
                "description": expense_data["description"],
                "group_id": expense_data["group_id"],
            }
        ).encode("utf-8")

        # Publish message
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()

        # Create HATEOAS links
        links = [
            {"rel": "self", "href": f"/api/expenses/{id}"},
            {"rel": "payments", "href": f"/api/expenses/{id}/payments"},
        ]

        response.headers["Link"] = f'</groups/{id}>; rel="created_resource"'
        return CreateExpenseResponse(expense_id=id, links=links)

    except Exception as e:
        print(repr(e))
        raise HTTPException(
            status_code=400, detail=f"An error occurred while creating the expense: {e}"
        )
