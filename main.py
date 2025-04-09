import os
import json
import questionary
from pprint import pprint
from api.users import create_users
from api.auth import login, LoginResult, auth
from schema.schema import CreateUser, User
from pydantic import BaseModel
from typing import Optional


class CurrentUserData(BaseModel):
    user_id: int = 0
    username: str = ""
    email: str = ""


class UserSession(BaseModel):
    cookie: Optional[str] = ""
    has_logged_in: bool = False
    previous_username: str = ""
    current_user_data: CurrentUserData = CurrentUserData()


class FinTrack:
    def __init__(self):
        self.user_session = UserSession()
        self.current_user: User = None
        self.save_file = "./cmd/save_data.json"
        self.clear_screen()
        self.sync_save_data()

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def sync_save_data(self):
        try:
            with open(self.save_file, "r") as f:
                data = json.load(f)
                pprint(data)
                self.user_session = UserSession(**data)
                if not self.user_session.has_logged_in:
                    return
                else:
                    result = auth(jwt=self.user_session.cookie)
                    if result.success:
                        self.current_user = result.result.user
                    else:
                        print("Authentication failed. Please log in again.")
                        self.user_session = UserSession()
                        self.save_save_data()
        except Exception as e:
            print(f"Error loading save data: {e}")

    def save_save_data(self):
        try:
            with open(self.save_file, "w") as f:
                json.dump(self.user_session.model_dump(), f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def main_menu(self):
        # self.clear_screen()
        pprint(self.user_session)

        while True:
            try:
                choice = questionary.select(
                    "What do you want to do?",
                    choices=["user", "income", "logout"],
                ).ask(kbi_msg="You exited from program.")

                if choice is None:
                    break

                if choice == "logout":
                    self.logout()

                # self.clear_screen()

                if choice == "user":
                    self.user_menu()
                elif choice == "income":
                    self.income_menu()
            except Exception as e:
                print(f"Unexpected error: {e}")

    def logout(self):
        self.user_session = UserSession()
        self.current_user = None
        self.save_save_data()
        print("Successfully logged out.")

    def user_menu(self):
        while True:
            try:
                action = questionary.select(
                    "What do you want to do in user menu?",
                    choices=[
                        "Create Account",
                        "View Account",
                        "Update Account Details",
                        "Delete Account",
                    ],
                ).ask(kbi_msg="You exited from user options menu.")

                if action is None:
                    break

                # self.clear_screen()

                if action == "View Account":
                    self.view_or_login_user()

                if action == "Create Account":
                    self.create_account_flow()

                if action == "Update Account Details":
                    self.create_account_flow()

                print(action)
            except Exception as e:
                print(f"User menu error: {e}")

    def update_user(self):
        print("Update user details coming soon!")

    def login_user(self):
        print("Login to your account")
        username_or_email = questionary.text("Enter Username or Email: ").ask()
        if username_or_email is None:
            return

        password = questionary.text(f"Enter Password for {username_or_email}: ").ask()
        if password is None:
            return

        res = login(username_or_email, password)
        if res.success:
            pprint(res.results)
            self.set_user_session(res.results)
            print(f"Logged in as {username_or_email}.")
        else:
            print(f"Login failed: {res.errorType} - {res.error}")

    def view_or_login_user(self):
        if self.user_session.has_logged_in:
            pprint(self.current_user)
            return

        try:
            print("You need to log in to view your account.")
            has_account = questionary.confirm("Do you have an account?").ask()
            if has_account is None:
                return

            if has_account:
                self.login_user()

            else:
                self.create_account_flow()

        except Exception as e:
            print(f"Login error: {e}")

    def create_account_flow(self):
        try:
            print("Create a new account")
            username = questionary.text("Enter Username: ").ask()
            if username is None:
                return

            email = questionary.text("Enter Email: ").ask()
            if email is None:
                return

            password = questionary.text(f"Enter Password for {username}: ").ask()
            if password is None:
                return

            results = create_users(
                [CreateUser(username=username, email=email, password=password)]
            )

            if results.success:
                print(f"Account created for {username}.")
                self.login_user()
            else:
                print(f"Account creation failed: {results.errorType} - {results.error}")

        except Exception as e:
            print(f"Account creation error: {e}")

    def set_user_session(self, login_result: LoginResult):
        self.current_user = login_result.user
        self.user_session = UserSession(
            **{
                "cookie": login_result.jwt,
                "has_logged_in": True,
                "previous_username": login_result.user.username,
                "current_user_data": {
                    "user_id": login_result.user.user_id,
                    "username": login_result.user.username,
                    "email": login_result.user.email,
                },
            }
        )
        self.save_save_data()

    def income_menu(self):
        print("Income menu coming soon!")


if __name__ == "__main__":
    app = FinTrack()
    app.main_menu()
