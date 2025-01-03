import logging
import time
import uvicorn
from ariadne.asgi import GraphQL
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from resources import (
    create_expense,
    get_expense_from_id,
    get_expense_from_payer,
    get_expense_from_payee,
    delete_expense,
    get_payment,
    get_payments,
    put_payment,
    delete_payment,
    create_expense_and_group,
    confirm_payment,
    get_payments_by_user,
)

app = FastAPI()

app.include_router(create_expense.router)
app.include_router(get_expense_from_id.router)
app.include_router(delete_expense.router)
app.include_router(get_payments.router)
app.include_router(get_payment.router)
app.include_router(put_payment.router)
app.include_router(delete_payment.router)
app.include_router(create_expense_and_group.router)
app.include_router(get_expense_from_payer.router)
app.include_router(get_expense_from_payee.router)
app.include_router(confirm_payment.router)

app.add_route("/graphql", GraphQL(get_payments_by_user.schema, debug=True))

# set up middleware logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# middleware to log requests before and after
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    # log before the request is processed
    start_time = time.time()

    # call the next process in the pipeline
    response = await call_next(request)

    # log after the request is processed
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} | Time: {process_time:.4f}s")

    return response


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace "*" with your UI's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_root():
    # GroupService info
    microservice_info = {
        "name": "Expense Service",
        "description": "Manages expense management and detail retrieval",
    }
    return microservice_info


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
