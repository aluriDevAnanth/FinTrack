# In services/savings_goals.py or similar

from datetime import date
from pprint import pprint
from py_backend.db.db import create_connection
from schema.schema import (
    BaseSuccessResponse,
    BaseErrorResponse,
    SavingsGoal,
    CreateSavingsGoal,
    UpdateSavingsGoal,
)
from pydantic import ValidationError
from mysql.connector import Error as MYSQLError

conn = create_connection()


class BaseSavingsGoalSuccessResponse(BaseSuccessResponse):
    result: SavingsGoal


class BaseSavingsGoalReadSuccessResponse(BaseSuccessResponse):
    result: list[SavingsGoal]


def create_savings_goal(
    goal_data: CreateSavingsGoal,
) -> BaseSavingsGoalSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            columns = list(goal_data.model_fields_set)
            placeholders = ",".join(["%s"] * len(columns))
            column_names = ", ".join(columns)
            values = tuple(getattr(goal_data, col) for col in columns)

            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                INSERT INTO savings_goals ({column_names}) VALUES ({placeholders})
                """,
                values,
            )
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            goal_id = cursor.fetchone()[0]

            cursor.execute(
                f"""-- sql
                SELECT {", ".join(SavingsGoal.model_fields.keys())} FROM savings_goals WHERE goal_id = %s
                """,
                (goal_id,),
            )
            goal = SavingsGoal(**dict(zip(cursor.column_names, cursor.fetchone())))
            cursor.close()

            return BaseSavingsGoalSuccessResponse(
                success=True,
                message="Savings goal created successfully",
                result=goal,
            )

    except (MYSQLError, ValidationError, Exception) as e:
        return BaseErrorResponse(
            success=False,
            errorType=type(e).__name__,
            error=str(e) if not isinstance(e, ValidationError) else e.json(),
        )


def read_savings_goals(
    user_id: int,
) -> BaseSavingsGoalReadSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                SELECT {", ".join(SavingsGoal.model_fields.keys())} FROM savings_goals WHERE user_id = %s
                """,
                (user_id,),
            )
            goals = [
                SavingsGoal(**dict(zip(cursor.column_names, row)))
                for row in cursor.fetchall()
            ]
            cursor.close()
            return BaseSavingsGoalReadSuccessResponse(
                success=True,
                message="Savings goals retrieved successfully",
                result=goals,
            )

    except (MYSQLError, ValidationError, Exception) as e:
        return BaseErrorResponse(
            success=False,
            errorType=type(e).__name__,
            error=str(e) if not isinstance(e, ValidationError) else e.json(),
        )


def read_savings_goal(
    goal_id: int,
) -> BaseSavingsGoalSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                SELECT {", ".join(SavingsGoal.model_fields.keys())} FROM savings_goals WHERE goal_id = %s
                """,
                (goal_id,),
            )
            result = cursor.fetchone()
            if not result:
                return BaseErrorResponse(
                    success=False, errorType="NotFound", error="Goal not found"
                )
            goal = SavingsGoal(**dict(zip(cursor.column_names, result)))
            cursor.close()
            return BaseSavingsGoalSuccessResponse(
                success=True,
                message="Savings goal retrieved successfully",
                result=goal,
            )

    except (MYSQLError, ValidationError, Exception) as e:
        return BaseErrorResponse(
            success=False,
            errorType=type(e).__name__,
            error=str(e) if not isinstance(e, ValidationError) else e.json(),
        )


def update_savings_goal(
    goal_data: UpdateSavingsGoal,
) -> BaseSavingsGoalSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            update_fields = goal_data.model_dump(exclude_unset=True)
            set_clause = ", ".join(
                [f"{key} = %s" for key in update_fields if key != "goal_id"]
            )
            values = tuple(
                update_fields[key] for key in update_fields if key != "goal_id"
            )

            cursor = conn.cursor()
            cursor.execute(
                f"""-- sql
                UPDATE savings_goals SET {set_clause} WHERE goal_id = %s
                """,
                values + (goal_data.goal_id,),
            )
            conn.commit()

            cursor.execute(
                f"""-- sql
                SELECT {", ".join(SavingsGoal.model_fields.keys())} FROM savings_goals WHERE goal_id = %s
                """,
                (goal_data.goal_id,),
            )
            goal = SavingsGoal(**dict(zip(cursor.column_names, cursor.fetchone())))
            cursor.close()

            return BaseSavingsGoalSuccessResponse(
                success=True,
                message="Savings goal updated successfully",
                result=goal,
            )

    except (MYSQLError, ValidationError, Exception) as e:
        return BaseErrorResponse(
            success=False,
            errorType=type(e).__name__,
            error=str(e) if not isinstance(e, ValidationError) else e.json(),
        )


def delete_savings_goal(goal_id: int) -> BaseSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM savings_goals WHERE goal_id = %s", (goal_id,))
            conn.commit()
            cursor.close()
            return BaseSuccessResponse(
                success=True,
                message="Savings goal deleted successfully",
                result=None,
            )

    except (MYSQLError, ValidationError, Exception) as e:
        return BaseErrorResponse(
            success=False,
            errorType=type(e).__name__,
            error=str(e) if not isinstance(e, ValidationError) else e.json(),
        )


# tests

""" Example usage:

pprint(
    create_savings_goal(
        CreateSavingsGoal(
            user_id=1,
            name="New Car",
            target_amount=25000,
            target_date=date(2025, 12, 31),
        )
    ).model_dump()
)

pprint(read_savings_goals(user_id=1).model_dump())

pprint(
    update_savings_goal(UpdateSavingsGoal(goal_id=1, current_amount=10000)).model_dump()
)

pprint(delete_savings_goal(goal_id=1).model_dump())

"""
