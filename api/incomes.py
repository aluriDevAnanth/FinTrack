from db.db import create_connection
from schema.schema import (
    CreateIncome,
    UpdateIncome,
    Income,
    BaseSuccessResponse,
    BaseErrorResponse,
)
from pydantic import ValidationError
from mysql.connector import Error as MYSQLError
from pprint import pprint
from hashlib import sha256

conn = create_connection()


class BaseIncomeSuccessResponse(BaseSuccessResponse):
    result: Income


class BaseIncomeReadSuccessResponse(BaseSuccessResponse):
    result: list[Income]


def create_income(
    income_create_data: CreateIncome,
) -> BaseIncomeSuccessResponse | BaseErrorResponse:

    try:
        if conn:
            str_placeholder = ",".join(
                ["%s"] * len(list(income_create_data.model_fields_set))
            )
            col_name_placeholder = ", ".join(list(income_create_data.model_fields_set))
            values = tuple(
                [
                    getattr(income_create_data, i)
                    for i in list(income_create_data.model_fields_set)
                ]
            )
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                insert into income ({col_name_placeholder}) values ({str_placeholder})
                """,
                values,
            )
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            last_insert_id = cursor.fetchone()[0]

            cursor.execute(
                f"""-- sql
                select {", ".join(list(Income.model_fields.keys()))} from income 
                where income_id = %s
                """,
                (last_insert_id,),
            )

            income = Income(**dict(zip(cursor.column_names, cursor.fetchone())))

            cursor.close()
            return BaseIncomeSuccessResponse(
                **{
                    "success": True,
                    "message": "Income created successfully",
                    "result": income,
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


def read_income_list(user_id: int):
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                select {", ".join(list(Income.model_fields.keys()))} from income 
                where user_id = %s
                """,
                (user_id,),
            )
            income_list = [
                Income(**dict(zip(cursor.column_names, i))) for i in cursor.fetchall()
            ]
            cursor.close()
            return BaseIncomeReadSuccessResponse(
                **{
                    "success": True,
                    "message": "Users created successfully",
                    "result": income_list,
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


def update_income(
    update_income_data: UpdateIncome,
) -> BaseIncomeSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()

            str_placeholder = ",".join(
                [
                    f"{i} = %s"
                    for i in list(update_income_data.model_dump(exclude_unset=True))
                ]
            )
            values = tuple(
                [
                    getattr(update_income_data, i)
                    for i in list(update_income_data.model_dump(exclude_unset=True))
                ]
            )
            cursor.execute(
                f"""-- sql
                    update income set {str_placeholder} where income_id = %s
                """,
                values + (update_income_data.income_id,),
            )

            conn.commit()

            cursor.execute(
                f"""-- sql
                    select {", ".join(list(Income.model_fields.keys()))} from income 
                    where income_id = %s
                """,
                (update_income_data.income_id,),
            )

            income = Income(**dict(zip(cursor.column_names, cursor.fetchone())))

            cursor.close()
            conn.close()
            return BaseIncomeSuccessResponse(
                **{
                    "success": True,
                    "message": "Users created successfully",
                    "result": income,
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


def delete_income(income_id: int) -> BaseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                    delete from income where income_id = %s
                """,
                (income_id,),
            )
            conn.commit()
            cursor.close()
            return BaseSuccessResponse(
                **{
                    "success": True,
                    "message": "Users created successfully",
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
