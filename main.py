import os
from cmd.user_session_manager import UserSessionManager
from cmd.user_cli import UserCLI
from colorama import init
import questionary

init(autoreset=True)


class FinTrack:
    def __init__(self):
        self.session_manager = UserSessionManager()
        self.session_manager.sync_user_session()
        self.user_cli = UserCLI(self.session_manager)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def main_menu(self):
        while True:
            choice = questionary.select(
                "What do you want to do?", choices=["user", "income", "logout"]
            ).ask()

            if choice is None:
                print("Exiting the application.")
                break

            if choice == "logout":
                self.session_manager.reset_session()
                print("Logged out.")
            elif choice == "user":
                self.user_cli.user_menu()
            elif choice == "income":
                print("Income menu coming soon!")


if __name__ == "__main__":
    app = FinTrack()
    app.main_menu()
