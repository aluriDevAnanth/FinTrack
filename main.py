import os
from cmd.user_session_manager import UserSessionManager
from cmd.user_cli import UserCLI
from colorama import init
import questionary
from cmd.income_cli import IncomeCLI
from cmd.expenses_cli import ExpensesCLI
from cmd.transactions_cli import TransactionsCLI
from cmd.budgets_cli import BudgetsCLI
from cmd.savings_goals_cli import SavingsGoalsCLI

init(autoreset=True)


class FinTrack:
    def __init__(self):
        self.session_manager = UserSessionManager()
        self.session_manager.sync_user_session()
        self.user_cli = UserCLI(self.session_manager)
        self.income_cli = IncomeCLI(self.session_manager)
        self.expense_cli = ExpensesCLI(self.session_manager)
        self.transaction_cli = TransactionsCLI(self.session_manager)
        self.budget_cli = BudgetsCLI(self.session_manager)
        self.savings_goal_cli = SavingsGoalsCLI(self.session_manager)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def main_menu(self):
        while True:
            choice = questionary.select(
                "What do you want to do?",
                choices=[
                    "user",
                    "income",
                    "expenses",
                    "transactions",
                    "budgets",
                    "savings goals",
                    "logout",
                ],
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
                self.income_cli.income_menu()
            elif choice == "expenses":
                self.expense_cli.expense_menu()
            elif choice == "transactions":
                self.transaction_cli.transaction_menu()
            elif choice == "budgets":
                self.budget_cli.budget_menu()
            elif choice == "savings goals":
                self.savings_goal_cli.savings_goal_menu()


if __name__ == "__main__":
    app = FinTrack()
    app.main_menu()
