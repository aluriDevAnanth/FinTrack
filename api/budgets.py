from db.db import create_connection
from schema.schema import (
    BaseSuccessResponse,
    BaseErrorResponse,
    Budget,
    CreateBudget,
    UpdateBudget,
)
from pydantic import ValidationError
from mysql.connector import Error as MYSQLError
from datetime import date
from pprint import pprint

conn = create_connection()


class BaseBudgetSuccessResponse(BaseSuccessResponse):
    result: Budget


class BaseBudgetReadSuccessResponse(BaseSuccessResponse):
    result: list[Budget]


def create_budget(
    budget_create_data: CreateBudget,
) -> BaseBudgetSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            str_placeholder = ",".join(
                ["%s"] * len(list(budget_create_data.model_fields_set))
            )
            col_name_placeholder = ", ".join(list(budget_create_data.model_fields_set))
            values = tuple(
                [
                    getattr(budget_create_data, i)
                    for i in list(budget_create_data.model_fields_set)
                ]
            )
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                INSERT INTO budgets ({col_name_placeholder}) VALUES ({str_placeholder})
                """,
                values,
            )
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            last_insert_id = cursor.fetchone()[0]

            cursor.execute(
                f"""-- sql
                SELECT {", ".join(list(Budget.model_fields.keys()))} FROM budgets 
                WHERE budget_id = %s
                """,
                (last_insert_id,),
            )

            budget = Budget(**dict(zip(cursor.column_names, cursor.fetchone())))

            cursor.close()
            return BaseBudgetSuccessResponse(
                **{
                    "success": True,
                    "message": "Budget created successfully",
                    "result": budget,
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
    except MYSQLError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": type(e).__name__, "error": str(e)}
        )


def read_budget_list(user_id: int) -> BaseBudgetReadSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                SELECT {", ".join(list(Budget.model_fields.keys()))} FROM budgets 
                WHERE user_id = %s
                """,
                (user_id,),
            )
            budget_list = [
                Budget(**dict(zip(cursor.column_names, i))) for i in cursor.fetchall()
            ]
            cursor.close()
            return BaseBudgetReadSuccessResponse(
                **{
                    "success": True,
                    "message": "Budgets retrieved successfully",
                    "result": budget_list,
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


def read_budget(budget_id: int) -> BaseBudgetSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                SELECT {", ".join(list(Budget.model_fields.keys()))} FROM budgets 
                WHERE budget_id = %s
                """,
                (budget_id,),
            )
            result = cursor.fetchone()
            if not result:
                return BaseErrorResponse(
                    **{
                        "success": False,
                        "errorType": "NotFound",
                        "error": "Budget not found",
                    }
                )

            budget = Budget(**dict(zip(cursor.column_names, result)))
            cursor.close()
            return BaseBudgetSuccessResponse(
                **{
                    "success": True,
                    "message": "Budget retrieved successfully",
                    "result": budget,
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


def update_budget(
    update_budget_data: UpdateBudget,
) -> BaseBudgetSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()

            str_placeholder = ",".join(
                [
                    f"{i} = %s"
                    for i in list(update_budget_data.model_dump(exclude_unset=True))
                ]
            )
            values = tuple(
                [
                    getattr(update_budget_data, i)
                    for i in list(update_budget_data.model_dump(exclude_unset=True))
                ]
            )
            cursor.execute(
                f"""-- sql
                    UPDATE budgets SET {str_placeholder} WHERE budget_id = %s
                """,
                values + (update_budget_data.budget_id,),
            )

            conn.commit()

            cursor.execute(
                f"""-- sql
                    SELECT {", ".join(list(Budget.model_fields.keys()))} FROM budgets 
                    WHERE budget_id = %s
                """,
                (update_budget_data.budget_id,),
            )

            budget = Budget(**dict(zip(cursor.column_names, cursor.fetchone())))

            cursor.close()
            return BaseBudgetSuccessResponse(
                **{
                    "success": True,
                    "message": "Budget updated successfully",
                    "result": budget,
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


def delete_budget(budget_id: int) -> BaseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                    DELETE FROM budgets WHERE budget_id = %s
                """,
                (budget_id,),
            )
            conn.commit()
            cursor.close()
            return BaseSuccessResponse(
                **{
                    "success": True,
                    "message": "Budget deleted successfully",
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


# tests

""" pprint(
    create_budget(
        CreateBudget(
            user_id=1,
            amount=5000,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
        )
    ).model_dump()
) """

# pprint(read_budget_list(user_id=1).model_dump())

# pprint(update_budget(UpdateBudget(budget_id=1, amount=100)).model_dump())

# pprint(delete_budget(budget_id=2).model_dump())
