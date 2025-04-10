import json

from colorama import Fore, Style
from schema.schema import User, CreateUser
from api.auth import auth
from pydantic import BaseModel
from typing import Optional
from pprint import pprint
from api.users import create_users
from api.auth import login
import questionary


class CurrentUserData(BaseModel):
    user_id: int = 0
    username: str = ""
    email: str = ""


class UserSession(BaseModel):
    cookie: Optional[str] = ""
    has_logged_in: bool = False
    previous_username: str = ""
    current_user_data: CurrentUserData = CurrentUserData()


class UserSessionManager:
    def __init__(self, save_file="./cli/save_data.json"):
        self.save_file = save_file
        self.user_session = UserSession()
        self.current_user: User = None

    def sync_user_session(self):
        try:
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.user_session = UserSession(**data)

                if not self.user_session.has_logged_in:
                    return

                result = auth(jwt=self.user_session.cookie)
                if result.success:
                    self.current_user = result.result.user
                else:
                    print(
                        Fore.RED
                        + Style.BRIGHT
                        + "Authentication failed. Please log in again."
                    )
                    self.reset_session()
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"{type(e).__name__}: {str(e)}")

    def save_user_session(self):
        try:
            with open(self.save_file, "w") as f:
                json.dump(self.user_session.model_dump(), f, indent=4)
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"{type(e).__name__}: {str(e)}")

    def reset_session(self):
        self.user_session = UserSession()
        self.current_user = None
        self.save_user_session()

    def login_user(self):
        username_or_email = questionary.text("Enter Username or Email: ").ask()
        password = questionary.password("Enter Password: ").ask()
        res = login(username_or_email, password)

        if res.success and res.results.user is not None:
            user = res.results.user
            self.current_user = user
            self.user_session.cookie = res.results.jwt
            self.user_session.has_logged_in = True
            self.user_session.previous_username = user.username
            self.user_session.current_user_data = CurrentUserData(
                **{
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                }
            )
            self.save_user_session()
            print(
                Fore.GREEN + Style.BRIGHT + f"Logged in as {self.current_user.username}"
            )
        else:
            print(Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}")

    def create_account_cli(self):
        try:
            print(Fore.CYAN + Style.BRIGHT + "Create a new account: ")
            username = questionary.text("Enter Username: ").ask()
            email = questionary.text("Enter Email: ").ask()
            password = questionary.password(f"Enter Password for {username}:   ").ask()
            cpassword = questionary.password(f"Confirm Password for {username}: ").ask()

            while password != cpassword:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + "Passwords do not match. Please try again."
                )
                password = questionary.password(
                    f"Enter Password for {username}:   "
                ).ask()
                cpassword = questionary.password(
                    f"Confirm Password for {username}: "
                ).ask()

            results = create_users(
                [CreateUser(username=username, email=email, password=password)]
            )
            if results.success:
                print(
                    Fore.GREEN
                    + Style.BRIGHT
                    + f"Account created sucessfully for {username}."
                )
                self.reset_session()
                print(
                    Fore.YELLOW
                    + Style.BRIGHT
                    + "You have been logged out. Please log in to your account."
                )
            else:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + f"Creation failed - {results.errorType}: {results.error}"
                )
                self.create_account_cli()
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"{type(e).__name__}: {str(e)}")

    def login_or_create_account(self):
        try:
            print(
                Fore.CYAN + Style.BRIGHT + "Please log in first to use that feature: "
            )
            if questionary.confirm("Do you have an account?").ask():
                self.login_user()
            else:
                self.create_account_cli()
                self.login_user()
        except Exception as e:
            print(
                f"Error during login or account creation - {type(e).__name__}: {str(e)}"
            )
