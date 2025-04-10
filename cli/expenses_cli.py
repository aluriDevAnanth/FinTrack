from colorama import init, Fore, Style
from api.expenses import (
    create_expense,
    read_expense_list,
    update_expense,
    delete_expense,
)
from schema.schema import CreateExpense, UpdateExpense
import questionary
from pprint import pprint
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
                ).ask(kbi_msg="Exited expenses menu.")
                if not action:
                    break

                getattr(self, action.lower().replace(" ", "_") + "_cli")()
            except Exception as e:
                print(Fore.RED + f"{type(e).__name__}: {str(e)}")

    def add_expense_cli(self):
        try:
            amount_input = questionary.text("Enter expense amount: ").ask()
            amount = float(amount_input)

            description = questionary.text("Description: ").ask()
            expense_date = questionary.text("Date (YYYY-MM-DD): ").ask()

            res = create_expense(
                CreateExpense(
                    user_id=self.session.current_user.user_id,
                    amount=amount,
                    description=description,
                    expense_date=expense_date,
                )
            )
            print(res.message if res.success else f"{res.errorType}: {res.error}")
        except Exception as e:
            print(Fore.RED + f"{type(e).__name__}: {str(e)}")

    def view_expenses_cli(self):
        try:
            res = read_expense_list(self.session.current_user.user_id)
            pprint(
                [i.model_dump() for i in res.result]
                if res.success
                else f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(Fore.RED + f"{type(e).__name__}: {str(e)}")

    def update_expense_cli(self):
        try:
            expense_id_input = questionary.text("Enter expense ID to update:").ask()
            if not expense_id_input:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + "Exited update expense as expense_id is mandatory field, so skipping this means no update will be done."
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

            print(res.message if res.success else f"{res.errorType}: {res.error}")
            pprint(res.result.model_dump() if res.success else None)

        except Exception as e:
            print(Fore.RED + f"{type(e).__name__}: {str(e)}")

    def delete_expense_cli(self):
        try:
            expense_id_input = questionary.text("Enter expense ID to delete:").ask()
            expense_id = int(expense_id_input)

            res = delete_expense(expense_id)
            print(res.message if res.success else f"{res.errorType}: {res.error}")
        except Exception as e:
            print(Fore.RED + f"{type(e).__name__}: {str(e)}")
