from db.db import create_connection
from schema.schema import (
    UserCreate,
    User,
    BaseSuccessResponse,
    BaseErrorResponse,
    UserUpdate,
)
from pydantic import ValidationError
from pprint import pprint
from mysql.connector import Error as MYSQLError
from hashlib import sha256

conn = create_connection()


class BaseUsersSuccessResponse(BaseSuccessResponse):
    results: list[User]


def create_users(
    user_create_data: list[UserCreate],
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
                [(ucd.username, ucd.email, ucd.password) for ucd in user_create_data],
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

            inserted_user = [User(**iud) for iud in inserted_user_data]
            cursor.close()
            return BaseUsersSuccessResponse(
                {"success": True, "message": "", "results": inserted_user}
            )
    except MYSQLError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": "MYSQLError", "error": str(e)}
        )
    except ValidationError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": "ValidationError", "error": e.json()}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": "Exception", "error": str(e)}
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
            **{"success": False, "errorType": "MYSQLError", "error": str(e)}
        )
    except ValidationError as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": "ValidationError", "error": e.json()}
        )
    except Exception as e:
        return BaseErrorResponse(
            **{"success": False, "errorType": "Exception", "error": str(e)}
        )
