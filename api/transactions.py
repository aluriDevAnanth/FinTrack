from db.db import create_connection
from schema.schema import (
    BaseSuccessResponse,
    BaseErrorResponse,
    Transaction,
    CreateTransaction,
    UpdateTransaction,
)
from pydantic import ValidationError
from mysql.connector import Error as MYSQLError
from datetime import date
from pprint import pprint

conn = create_connection()


class BaseTransactionSuccessResponse(BaseSuccessResponse):
    result: Transaction


class BaseTransactionReadSuccessResponse(BaseSuccessResponse):
    result: list[Transaction]


def create_transaction(
    transaction_create_data: CreateTransaction,
) -> BaseTransactionSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            str_placeholder = ",".join(
                ["%s"] * len(list(transaction_create_data.model_fields_set))
            )
            col_name_placeholder = ", ".join(
                list(transaction_create_data.model_fields_set)
            )
            values = tuple(
                [
                    getattr(transaction_create_data, i)
                    for i in list(transaction_create_data.model_fields_set)
                ]
            )
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                INSERT INTO transactions ({col_name_placeholder}) VALUES ({str_placeholder})
                """,
                values,
            )
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            last_insert_id = cursor.fetchone()[0]

            cursor.execute(
                f"""-- sql
                SELECT {", ".join(list(Transaction.model_fields.keys()))} FROM transactions 
                WHERE transaction_id = %s
                """,
                (last_insert_id,),
            )

            transaction = Transaction(
                **dict(zip(cursor.column_names, cursor.fetchone()))
            )

            cursor.close()
            return BaseTransactionSuccessResponse(
                **{
                    "success": True,
                    "message": "Transaction created successfully",
                    "result": transaction,
                }
            )
    except MYSQLError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )
    except ValidationError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": e.json()}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )


def read_transaction_list(transaction_id: int):
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                SELECT {", ".join(list(Transaction.model_fields.keys()))} FROM transactions 
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )
            transaction_list = [
                Transaction(**dict(zip(cursor.column_names, i)))
                for i in cursor.fetchall()
            ]
            cursor.close()
            return BaseTransactionReadSuccessResponse(
                **{
                    "success": True,
                    "message": "Transactions retrieved successfully",
                    "result": transaction_list,
                }
            )
    except MYSQLError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )
    except ValidationError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": e.json()}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )


def update_transaction(
    update_transaction_data: UpdateTransaction,
) -> BaseTransactionSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()

            str_placeholder = ",".join(
                [
                    f"{i} = %s"
                    for i in list(
                        update_transaction_data.model_dump(exclude_unset=True)
                    )
                ]
            )
            values = tuple(
                [
                    getattr(update_transaction_data, i)
                    for i in list(
                        update_transaction_data.model_dump(exclude_unset=True)
                    )
                ]
            )
            cursor.execute(
                f"""-- sql
                    UPDATE transactions SET {str_placeholder} WHERE transaction_id = %s
                """,
                values + (update_transaction_data.transaction_id,),
            )

            conn.commit()

            cursor.execute(
                f"""-- sql
                    SELECT {", ".join(list(Transaction.model_fields.keys()))} FROM transactions 
                    WHERE transaction_id = %s
                """,
                (update_transaction_data.transaction_id,),
            )

            transaction = Transaction(
                **dict(zip(cursor.column_names, cursor.fetchone()))
            )

            cursor.close()
            return BaseTransactionSuccessResponse(
                **{
                    "success": True,
                    "message": "Transaction updated successfully",
                    "result": transaction,
                }
            )

    except MYSQLError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )
    except ValidationError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": e.json()}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )


def delete_transaction(transaction_id: int) -> BaseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                    DELETE FROM transactions WHERE transaction_id = %s
                """,
                (transaction_id,),
            )
            conn.commit()
            cursor.close()
            return BaseSuccessResponse(
                **{
                    "success": True,
                    "message": "Transaction deleted successfully",
                    "result": None,
                }
            )
    except MYSQLError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )
    except ValidationError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": e.json()}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )
