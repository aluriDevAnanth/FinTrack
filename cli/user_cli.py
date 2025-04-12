import questionary
from colorama import Fore, Style
from pprint import pprint
from py_backend.api.users import update_user, delete_user
from schema.schema import UpdateUser
from cli.user_session_manager import UserSessionManager


class UserCLI:
    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def user_menu(self):
        try:
            while True:
                action = questionary.select(
                    "What do you want to do in user menu?",
                    choices=[
                        "Create Account",
                        "View Account",
                        "Update Account",
                        "Delete Account",
                    ],
                ).ask(kbi_msg="Exited user menu.")

                if action is None:
                    break

                if (
                    not self.session.user_session.has_logged_in
                    and action != "Create Account"
                ):
                    self.session.login_or_create_account()

                getattr(self, action.lower().replace(" ", "_") + "_cli")()
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in user_menu] {type(e).__name__}: {str(e)}"
            )

    def create_account_cli(self):
        try:
            self.session.create_account_cli()
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in create_account_cli] {type(e).__name__}: {str(e)}"
            )

    def view_account_cli(self):
        try:
            pprint(self.session.current_user.model_dump())
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in view_account_cli] {type(e).__name__}: {str(e)}"
            )

    def update_account_cli(self):
        try:

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
                self.session.user_session.current_user_data.username = res.results[
                    0
                ].username
                self.session.user_session.current_user_data.email = res.results[0].email
                self.session.save_user_session()
                print("Updated successfully.")
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in update_account_cli] {type(e).__name__}: {str(e)}"
            )

    def delete_account_cli(self):
        try:
            confirm = questionary.text(
                "Type 'delete' to confirm account deletion: "
            ).ask()
            if confirm != "delete":
                print(Fore.RED + "Cancelled.")
                return

            res = delete_user(self.session.current_user.user_id)
            if res.success:
                print(Fore.RED + f"{self.session.current_user.username} deleted.")
                self.session.reset_session()
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in delete_account_cli] {type(e).__name__}: {str(e)}"
            )
