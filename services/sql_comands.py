import pymysql
from dotenv import load_dotenv
import os

# Use our .env file to set up the environment variables.
load_dotenv()


class SQLMachine:
    def create_connection(self):
        """
        Creates a connection to the SQL database specified by the
        environment variables.

        Returns the connection.
        """
        connection = pymysql.connect(
            unix_socket=f"/cloudsql/{os.getenv('DATABASE_IP')}",
            port=int(os.getenv("DATABASE_PORT")),
            user=os.getenv("DATABASE_UNAME"),
            passwd=os.getenv("DATABASE_PWORD"),
            autocommit=True,
        )
        return connection

    def select(self, schema, table, data=None):
        """
        Select everything from a certain table in a schema within
        the database.
        """

        if data is not None:
            conditions = [f"{x} = %s" for x in data]
            conditions = " AND ".join(conditions)
            query = f"SELECT * FROM {schema}.{table} WHERE {conditions}"
            values = tuple(data.values())
        else:
            # construct our query.
            query = f"SELECT * FROM {schema}.{table}"
            values = ()

        connection = self.create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()

        connection.close()

        return result

    def select_paginated(self, schema, table, limit, offset):
        """
        Select a limited number of entries from a table in a schema within
        the database.
        """

        query = f"SELECT * FROM {schema}.{table} LIMIT %s OFFSET %s"
        count_query = f"SELECT COUNT(*) FROM {schema}.{table}"

        connection = self.create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (limit, offset))
            paginated_results = cursor.fetchall()

            cursor.execute(count_query)
            total_count = cursor.fetchone()[0]

        connection.close()

        return {"results": paginated_results, "total_count": total_count}

    def insert(self, schema, table, data):
        columns = ", ".join([f"`{col}`" for col in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))

        query = f"INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders})"

        connection = self.create_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, tuple(data.values()))
            id = cursor.lastrowid

        connection.close()

        return id

    def update(self, schema, table, condition, data):
        """
        Update the data in schema.table according to condition.
        Returns the number of affected rows.
        """

        conditions = [f"{x} = %s" for x in condition]
        conditions = " AND ".join(conditions)

        set_columns = [f"{x} = %s" for x in data]
        set_columns = ", ".join(set_columns)

        query = f"UPDATE {schema}.{table} SET {set_columns} WHERE {conditions}"

        values = list(data.values())
        values.extend(list(condition.values()))

        connection = self.create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.rowcount

        connection.close()

        return result

    def delete(self, schema, table, data=None):
        """
        Delete all rows from the table which meet the conditions.
        """

        if data is not None:
            conditions = [f"{x} = %s" for x in data]
            conditions = " AND ".join(conditions)
            query = f"DELETE FROM {schema}.{table} WHERE {conditions}"
            values = list(data.values())
        else:
            # construct our query.
            query = f"DELETE FROM {schema}.{table}"  # lowkey you should not even be able to do this 😭

        connection = self.create_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.rowcount

        connection.close()

        return result
