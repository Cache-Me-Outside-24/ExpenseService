from ariadne import QueryType, gql, make_executable_schema
from services.sql_comands import SQLMachine

# Define your GraphQL schema
type_defs = gql(
    """
    type Payment {
        expenseId: Int
        payerId: String
        amountOwed: Float
        paid: Boolean
        method: String
        groupId: Int
        groupName: String
        payeeName: String
    }

    type Query {
        payments(userId: String!): [Payment!]!
    }
"""
)

# Resolver for the "payments" query
query = QueryType()


@query.field("payments")
def resolve_payments(_, info, userId):
    sql = SQLMachine()

    # Fetch payments for the user
    payments_result = sql.select("expense_service_db", "payments", {"payer_id": userId})
    if not payments_result:
        return []

    payments = []
    for payment in payments_result:
        # Fetch group details
        group_details = sql.select(
            "group_service_db", "groups", {"group_id": payment[5]}
        )
        group_name = group_details[0][1] if group_details else "Unknown"
        # Fetch payee name
        user_details = sql.select("user_service_db", "users", {"id": payment[6]})

        payee_name = user_details[0][2] if user_details else "Unknown"

        payments.append(
            {
                "expenseId": payment[0],
                "payerId": payment[1],
                "amountOwed": payment[2],
                "paid": payment[3],
                "method": payment[4],
                "groupId": payment[5],
                "groupName": group_name,
                "payeeName": payee_name,
            }
        )

    return payments


# Create the Ariadne executable schema
schema = make_executable_schema(type_defs, query)
