from db.db import create_connection
from schema.schema import (
    CreateExpense,
    UpdateExpense,
    Expense,
    BaseSuccessResponse,
    BaseErrorResponse,
)
from pydantic import ValidationError
from mysql.connector import Error as MYSQLError
from pprint import pprint
from datetime import date

conn = create_connection()


class BaseExpenseSuccessResponse(BaseSuccessResponse):
    result: Expense


class BaseExpenseReadSuccessResponse(BaseSuccessResponse):
    result: list[Expense]


def create_expense(
    expense_create_data: CreateExpense,
) -> BaseExpenseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            str_placeholder = ",".join(
                ["%s"] * len(list(expense_create_data.model_fields_set))
            )
            col_name_placeholder = ", ".join(list(expense_create_data.model_fields_set))
            values = tuple(
                [
                    getattr(expense_create_data, i)
                    for i in list(expense_create_data.model_fields_set)
                ]
            )
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                insert into expenses ({col_name_placeholder}) values ({str_placeholder})
                """,
                values,
            )
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            last_insert_id = cursor.fetchone()[0]

            cursor.execute(
                f"""-- sql
                select {", ".join(list(Expense.model_fields.keys()))} from expenses 
                where expense_id = %s
                """,
                (last_insert_id,),
            )

            expense = Expense(**dict(zip(cursor.column_names, cursor.fetchone())))

            cursor.close()
            return BaseExpenseSuccessResponse(
                **{
                    "success": True,
                    "message": "Expense created successfully",
                    "result": expense,
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


def read_expense_list(user_id: int):
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                select {", ".join(list(Expense.model_fields.keys()))} from expenses 
                where user_id = %s
                """,
                (user_id,),
            )
            expense_list = [
                Expense(**dict(zip(cursor.column_names, i))) for i in cursor.fetchall()
            ]
            cursor.close()
            return BaseExpenseReadSuccessResponse(
                **{
                    "success": True,
                    "message": "Expenses retrieved successfully",
                    "result": expense_list,
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


def update_expense(
    update_expense_data: UpdateExpense,
) -> BaseExpenseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()

            str_placeholder = ",".join(
                [
                    f"{i} = %s"
                    for i in list(update_expense_data.model_dump(exclude_unset=True))
                ]
            )
            values = tuple(
                [
                    getattr(update_expense_data, i)
                    for i in list(update_expense_data.model_dump(exclude_unset=True))
                ]
            )
            cursor.execute(
                f"""-- sql
                    update expenses set {str_placeholder} where expense_id = %s
                """,
                values + (update_expense_data.expense_id,),
            )

            conn.commit()

            cursor.execute(
                f"""-- sql
                    select {", ".join(list(Expense.model_fields.keys()))} from expenses 
                    where expense_id = %s
                """,
                (update_expense_data.expense_id,),
            )

            expense = Expense(**dict(zip(cursor.column_names, cursor.fetchone())))

            cursor.close()
            conn.close()
            return BaseExpenseSuccessResponse(
                **{
                    "success": True,
                    "message": "Expense updated successfully",
                    "result": expense,
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


def delete_expense(expense_id: int) -> BaseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                    delete from expenses where expense_id = %s
                """,
                (expense_id,),
            )
            conn.commit()
            cursor.close()
            return BaseSuccessResponse(
                **{
                    "success": True,
                    "message": "Expense deleted successfully",
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
