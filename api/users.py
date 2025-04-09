from db.db import create_connection
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
                print(len(read_usernames), len(read_users_data))
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


def update_users(
    update_users_data: list[UpdateUser],
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
        if not update_users_data:
            return BaseErrorResponse(
                success=False,
                errorType="ValidationError",
                error="No update data provided",
            )

        if conn:
            cursor = conn.cursor()
            results: list[User] = []

            for uud in update_users_data:
                update_user = uud.model_dump()
                update_user.pop("user_id", None)

                if "password" in update_user and update_user["password"]:
                    update_user["password_hash"] = sha256(
                        update_user["password"].encode()
                    ).hexdigest()
                    update_user.pop("password", None)
                else:
                    update_user["password_hash"] = None

                placeholders = [
                    f"{k} = %s" for k, v in update_user.items() if v is not None
                ]

                values = [v for k, v in update_user.items() if v is not None]
                values.append(uud.user_id)

                sql_str = f"""-- sql
                        update users set {", ".join(placeholders)} where user_id = %s                
                    """
                cursor.execute(sql_str, tuple(values))
                conn.commit()

                cursor.execute(
                    """-- sql
                    select user_id, username, email, password_hash, created_at, updated_at from users 
                    where user_id = %s
                    """,
                    (uud.user_id,),
                )
                update_user_data = dict(zip(columns, cursor.fetchone()))
                results.append(User(**update_user_data))

            cursor.close()

            return BaseUsersSuccessResponse(
                success=True,
                message="Users updated successfully",
                results=results,
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
        print(e)
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=str(e)
        )


def delete_users(
    delete_user_ids: list[str],
) -> BaseUsersSuccessResponse | BaseErrorResponse:
    try:
        if not delete_user_ids:
            return BaseErrorResponse(
                success=False,
                errorType="ValidationError",
                error="No delete id data provided",
            )

        if conn:
            cursor = conn.cursor()

            sql_str = f"""-- sql
                delete from users where username in ({", ".join(["%s"] * len(delete_user_ids))})            
            """
            cursor.execute(sql_str, tuple(delete_user_ids))
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
        print(e)
        return BaseErrorResponse(
            success=False, errorType=type(e).__name__, error=str(e)
        )
