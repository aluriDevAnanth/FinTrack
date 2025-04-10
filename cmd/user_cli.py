import questionary
from colorama import Fore, Style
from pprint import pprint
from api.users import create_users, update_user, delete_user
from api.auth import login
from schema.schema import CreateUser, UpdateUser
from cmd.user_session_manager import UserSessionManager, CurrentUserData


class UserCLI:

    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def user_menu(self):
        while True:
            action = questionary.select(
                "What do you want to do in user menu?",
                choices=[
                    "Create Account",
                    "View Account",
                    "Update Account Details",
                    "Delete Account",
                ],
            ).ask(kbi_msg="Exited user menu.")

            if action is None:
                break
            getattr(self, action.lower().replace(" ", "_") + "_cli")()

    def view_account_cli(self):
        if self.session.user_session.has_logged_in:
            pprint(self.session.current_user)
        else:
            self.view_or_login_user()

    def create_account_cli(self):
        print("Create a new account")
        username = questionary.text("Enter Username: ").ask()
        email = questionary.text("Enter Email: ").ask()
        password = questionary.text(f"Enter Password for {username}: ").ask()

        results = create_users(
            [CreateUser(username=username, email=email, password=password)]
        )
        if results.success:
            print(f"Account created for {username}.")
            self.session.reset_session()
            print(
                Fore.YELLOW
                + Style.BRIGHT
                + "You have been logged out. Please log in to your account."
            )
            self.login_user()
        else:
            print(f"Creation failed: {results.errorType} - {results.error}")

    def update_account_details_cli(self):
        self.view_or_login_user()
        user = self.session.current_user
        data = UpdateUser(user_id=user.user_id)

        username = questionary.text("Enter New Username: ").ask()
        if username:
            data.username = username

        email = questionary.text("Enter New Email: ").ask()
        if email:
            data.email = email

        while True:
            password = questionary.password("Enter New Password: ").ask()
            if not password:
                break
            cpassword = questionary.password("Confirm Password: ").ask()
            if password == cpassword:
                data.password = password
                break
            print("Passwords do not match.")

        res = update_user(data)
        if res.success:
            self.session.current_user = res.results[0]
            pprint(self.session.current_user)
            self.session.user_session.current_user_data.username = res.results[
                0
            ].username
            self.session.user_session.current_user_data.email = res.results[0].email
            self.session.save_user_session()
            print("Updated successfully.")

    def delete_account_cli(self):
        self.view_or_login_user()
        confirm = questionary.text("Type 'delete' to confirm account deletion: ").ask()
        if confirm != "delete":
            print(Fore.RED + "Cancelled.")
            return

        res = delete_user(self.session.current_user.user_id)
        if res.success:
            print(Fore.RED + f"{self.session.current_user.username} deleted.")
            self.session.reset_session()

    def login_user(self):
        username_or_email = questionary.text("Enter Username or Email: ").ask()
        password = questionary.password("Enter Password: ").ask()
        res = login(username_or_email, password)

        if res.success and res.results.user is not None:
            user = res.results.user
            self.session.current_user = user
            self.session.user_session.cookie = res.results.jwt
            self.session.user_session.has_logged_in = True
            self.session.user_session.previous_username = user.username
            self.session.user_session.current_user_data = CurrentUserData(
                **{
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                }
            )
            self.session.save_user_session()
            print(f"Logged in as {user.username}")
        else:
            print(f"Login failed: {res.errorType} - {res.error}")

    def view_or_login_user(self):
        if self.session.user_session.has_logged_in:
            pprint(self.session.current_user)
        else:
            print(Fore.RED + "Please log in.")
            if questionary.confirm("Do you have an account?").ask():
                self.login_user()
            else:
                self.create_account_cli()
