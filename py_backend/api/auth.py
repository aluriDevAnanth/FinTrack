from py_backend.db.db import create_connection
from hashlib import sha256
from schema.schema import User, BaseErrorResponse, BaseSuccessResponse
from mysql.connector import Error as MYSQLError
from pydantic import ValidationError
from pprint import pprint
from jwt import encode as jwt_encode, decode as jwt_decode
from os import getenv as os_getenv
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone


class LoginResult(BaseModel):
    user: User
    jwt: str


class AuthResult(BaseModel):
    user: User


class LoginSuccessResponse(BaseSuccessResponse):
    results: LoginResult


class AuthSuccessResponse(BaseSuccessResponse):
    result: AuthResult


conn = create_connection()


def login(
    username_or_email: str, password: str
) -> LoginSuccessResponse | BaseErrorResponse:
    try:
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """-- sql
                    select user_id, username, email, password_hash, created_at, updated_at from users
                    where username = %s or email = %s
                """,
                (username_or_email, username_or_email),
            )

            user = cursor.fetchone()

            return LoginSuccessResponse(
                **{
                    "success": True,
                    "message": "Users created successfully",
                    "results": {
                        "user": User(
                            **dict(zip([i for i in User.model_fields.keys()], user))
                        ),
                        "jwt": jwt_encode(
                            {
                                "user_id": user[0],
                                "username": user[1],
                                "email": user[2],
                                "exp": datetime.now(tz=timezone.utc)
                                + timedelta(days=3),
                            },
                            key=os_getenv("JWT_SECRET_KEY"),
                            algorithm="HS256",
                        ),
                    },
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


def auth(jwt: str) -> AuthSuccessResponse | BaseErrorResponse:
    try:
        user_data = jwt_decode(jwt, os_getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        print(user_data)

        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """-- sql
                    select user_id, username, email, password_hash, created_at, updated_at from users
                    where username = %s 
                """,
                (user_data["username"],),
            )

            user = cursor.fetchone()

            return AuthSuccessResponse(
                **{
                    "success": True,
                    "message": "User authenticated successfully",
                    "result": {
                        "user": User(
                            **dict(zip([i for i in User.model_fields.keys()], user))
                        ),
                    },
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
