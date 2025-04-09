from api.users import create_users, read_users, update_users, delete_users
from schema.schema import CreateUser, UpdateUser
from faker import Faker
from pprint import pprint
from hashlib import sha256
import pytest
from db.db import create_connection

fake = Faker()


def test_create_users():
    create_users_data = {
        "email": fake.email(),
        "password": fake.password(),
        "username": fake.name(),
    }
    res = create_users([CreateUser(**create_users_data)])

    if res.success:
        user = res.results[0]
        assert user.username == create_users_data["username"]
        assert user.email == create_users_data["email"]
        assert (
            user.password_hash
            == sha256(create_users_data["password"].encode()).hexdigest()
        )
    else:
        pytest.fail(f"{res.errorType}: {res.error}")


def test_read_users():
    read_usernames = ["Timothy Frazier", "Jacqueline Shaw"]
    results = read_users(read_usernames)

    if results.success:
        users = [res.model_dump() for res in results.results]
        pprint(users)
        for user in users:
            assert user["username"] in read_usernames
    else:
        pytest.fail(f"{results.errorType}: {results.error}")


def test_update_users():
    update_users_data = {"user_id": 1, "username": "qqq", "email": "qqq@qqq.com"}
    results = update_users([UpdateUser(**update_users_data)])

    if results.success:
        users = results.results
        check_columns = [i for i in update_users_data.keys()]
        check_columns.remove("user_id")
        for user in users:
            for cc in check_columns:
                assert getattr(user, cc) == update_users_data[cc]
    else:
        pytest.fail(f"{results.errorType}: {results.error}")


def test_delete_users():
    results = delete_users(["Mark James", "Timothy Wright"])

    if results.success:
        assert results.success
    else:
        pytest.fail(f"{results.errorType}: {results.error}")


def test_connection_with_db():
    conn = create_connection()
    assert conn is not None
    assert conn.is_connected()
    assert conn.database == "testing_fin_track"
    conn.close()
