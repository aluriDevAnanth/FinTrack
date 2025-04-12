from colorama import init, Fore, Style
from py_backend.api.expenses import (
    create_expense,
    read_expense_list,
    update_expense,
    delete_expense,
)
from schema.schema import CreateExpense, UpdateExpense
import questionary
from pprint import pprint
from datetime import date
from cli.user_session_manager import UserSessionManager

init(autoreset=True)


class ExpensesCLI:
    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def expenses_menu(self):
        while True:
            try:
                action = questionary.select(
                    "Expenses Menu",
                    choices=[
                        "Add Expense",
                        "View Expenses",
                        "Update Expense",
                        "Delete Expense",
                    ],
                ).ask(kbi_msg="")
                if not action:
                    break

                getattr(self, action.lower().replace(" ", "_") + "_cli")()
            except Exception as e:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + f"[Exception in expenses_menu] {type(e).__name__}: {str(e)}"
                )

    def add_expense_cli(self):
        try:
            amount = float(questionary.text("Enter expense amount: ").ask())
            description = questionary.text("Description: ").ask()
            expense_date_input = questionary.text(
                "Date (YYYY-MM-DD) (Leave blank for today): "
            ).ask()
            expense_date = (
                date.fromisoformat(expense_date_input)
                if expense_date_input
                else date.today()
            )

            expense_create_data = CreateExpense(
                user_id=self.session.current_user.user_id,
                amount=amount,
                description=description,
                expense_date=expense_date,
            )

            if expense_date:
                expense_create_data.expense_date = expense_date

            res = create_expense(expense_create_data)
            print(
                res.message
                if res.success
                else f"[Exception from API in add_expense_cli] {res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in add_expense_cli] {type(e).__name__}: {str(e)}"
            )

    def view_expenses_cli(self):
        try:
            res = read_expense_list(self.session.current_user.user_id)
            pprint(
                [i.model_dump() for i in res.result]
                if res.success
                else f"[Exception from API in view_expenses_cli] {res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in view_expenses_cli] {type(e).__name__}: {str(e)}"
            )

    def update_expense_cli(self):
        try:
            expense_id_input = questionary.text("Enter expense ID to update:").ask()
            if not expense_id_input:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + "Exited update expense as expense_id is mandatory field."
                )
                return

            expense_id = int(expense_id_input)
            update_expense_data = UpdateExpense(
                expense_id=expense_id, user_id=self.session.current_user.user_id
            )

            amount_input = questionary.text("New amount:").ask()
            if amount_input:
                update_expense_data.amount = float(amount_input)

            description = questionary.text("New description:").ask()
            if description:
                update_expense_data.description = description

            expense_date = questionary.text("New expense_date:").ask()
            if expense_date:
                update_expense_data.expense_date = expense_date

            res = update_expense(update_expense_data)

            print(
                res.message
                if res.success
                else f"[Exception from API in update_expense_cli] {res.errorType}: {res.error}"
            )
            pprint(res.result.model_dump() if res.success else None)

        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in update_expense_cli] {type(e).__name__}: {str(e)}"
            )

    def delete_expense_cli(self):
        try:
            expense_id = int(questionary.text("Enter expense ID to delete:").ask())
            res = delete_expense(expense_id)
            print(
                res.message
                if res.success
                else f"[Exception from API in delete_expense_cli] {res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in delete_expense_cli] {type(e).__name__}: {str(e)}"
            )
