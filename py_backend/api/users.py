from py_backend.db.db import create_connection
from schema.schema import (
    CreateUser,
    User,
    BaseSuccessResponse,
    BaseErrorResponse,
    UpdateUser,
)
from pydantic import ValidationError
from pprint import pprint
from mysql.connector import Error as MYSQLError
from hashlib import sha256

conn = create_connection()


class BaseUsersSuccessResponse(BaseSuccessResponse):
    results: list[User]


def create_users(
    user_create_data: list[CreateUser],
) -> BaseUsersSuccessResponse | BaseErrorResponse:
    columns = [
        "user_id",
        "username",
        "email",
        "password_hash",
        "created_at",
        "updated_at",
    ]

    try:
        if conn:
            cursor = conn.cursor()
            cursor.executemany(
                """-- sql
                insert into users (username, email, password_hash)  values (%s,%s,%s) 
                """,
                [
                    (ucd.username, ucd.email, sha256(ucd.password.encode()).hexdigest())
                    for ucd in user_create_data
                ],
            )
            conn.commit()

            inserted_usernames = [ucd.username for ucd in user_create_data]
            placeholder = ",".join(["%s"] * len(inserted_usernames))
            cursor.execute(
                f"""-- sql
                select user_id, username, email, password_hash, created_at, updated_at from users 
                where username in ({placeholder})
                """,
                tuple(inserted_usernames),
            )
            inserted_user_data = [dict(zip(columns, i)) for i in cursor.fetchall()]

            if not inserted_user_data:
                return BaseErrorResponse(
                    **{
                        "success": False,
                        "errorType": "NotFound",
                        "error": "No users found",
                    }
                )

            inserted_users = [User(**iud) for iud in inserted_user_data]
            cursor.close()
            return BaseUsersSuccessResponse(
                **{
                    "success": True,
                    "message": "Users created successfully",
                    "results": inserted_users,
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


def read_users(
    read_usernames: list[str],
) -> BaseUsersSuccessResponse | BaseErrorResponse:
    columns = [
        "user_id",
        "username",
        "email",
        "password_hash",
        "created_at",
        "updated_at",
    ]

    try:
        if conn:
            cursor = conn.cursor()
            placeholder = ",".join(["%s"] * len(read_usernames))
            cursor.execute(
                f"""-- sql
                    select user_id, username, email, password_hash, created_at, updated_at from users 
                    where username in ({placeholder})
                """,
                tuple(read_usernames),
            )
            read_users_data = [dict(zip(columns, i)) for i in cursor.fetchall()]

            if not read_users_data:
                return BaseErrorResponse(
                    **{
                        "success": False,
                        "errorType": "NotFound",
                        "error": "No users found",
                    }
                )

            if len(read_usernames) > len(read_users_data):
                return BaseErrorResponse(
                    **{
                        "success": False,
                        "errorType": "NotFound",
                        "error": "Some users not found",
                    }
                )

            read_users = [User(**rud) for rud in read_users_data]
            cursor.close()
            return BaseUsersSuccessResponse(
                **{"success": True, "message": "", "results": read_users}
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


def update_user(
    update_users_data: UpdateUser,
) -> BaseUsersSuccessResponse | BaseErrorResponse:
    try:
        if not update_users_data or not update_users_data.model_fields_set:
            return BaseErrorResponse(
                success=False,
                errorType="ValidationError",
                error="No update data provided",
            )

        if not conn:
            return BaseErrorResponse(
                success=False,
                errorType="MYSQLError",
                error="Failed to connect to DB",
            )

        cursor = conn.cursor()

        fields_to_update = update_users_data.model_fields_set - {"user_id"}
        if not fields_to_update:
            return BaseErrorResponse(
                success=False,
                errorType="ValidationError",
                error="No updatable fields provided",
            )

        set_clause = ", ".join([f"{field} = %s" for field in fields_to_update])
        values = tuple(getattr(update_users_data, field) for field in fields_to_update)

        update_query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
        print(update_query, values + (update_users_data.user_id,))

        cursor.execute(update_query, values + (update_users_data.user_id,))
        conn.commit()

        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s", (update_users_data.user_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return BaseErrorResponse(
                success=False,
                errorType="NotFoundError",
                error="User not found after update",
            )

        columns = [desc[0] for desc in cursor.description]
        user_data = dict(zip(columns, row))
        user = User(**user_data)

        cursor.close()

        return BaseUsersSuccessResponse(
            success=True,
            message="User updated successfully",
            results=[user],
        )

    except MYSQLError as e:
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=str(e)
        )
    except ValidationError as e:
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=e.json()
        )
    except Exception as e:
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=str(e)
        )


def delete_user(
    delete_user_id: int,
) -> BaseUsersSuccessResponse | BaseErrorResponse:
    try:
        if not delete_user_id:
            return BaseErrorResponse(
                success=False,
                errorType="ValidationError",
                error="No delete id data provided",
            )

        if conn:
            cursor = conn.cursor()

            sql_str = f"""-- sql
                delete from users where user_id  = %s            
            """
            cursor.execute(sql_str, (delete_user_id,))
            conn.commit()
            cursor.close()

            return BaseUsersSuccessResponse(
                success=True,
                message="Users updated successfully",
                results=[],
            )
        else:
            return BaseErrorResponse(
                success=False,
                errorType="MYSQLError",
                error="Failder to connect to DB",
            )
    except MYSQLError as e:
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=str(e)
        )
    except ValidationError as e:
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=e.json()
        )
    except Exception as e:
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=str(e)
        )
