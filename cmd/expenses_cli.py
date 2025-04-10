from api.expenses import (
    create_expense,
    read_expense_list,
    update_expense,
    delete_expense,
)
from schema.schema import CreateExpense, UpdateExpense
import questionary
from pprint import pprint


class ExpensesCLI:
    def __init__(self, session_manager):
        self.session = session_manager

    def expenses_menu(self):
        while True:
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

    def add_expense_cli(self):
        amount = float(questionary.text("Enter expense amount:").ask())
        category = questionary.text("Category:").ask()
        date = questionary.text("Date (YYYY-MM-DD):").ask()

        res = create_expense(
            CreateExpense(
                user_id=self.session.current_user.user_id,
                amount=amount,
                category=category,
                date=date,
            )
        )
        print(res.message if res.success else res.error)

    def view_expenses_cli(self):
        res = read_expense_list(self.session.current_user.user_id)
        pprint(res.result if res.success else res.error)

    def update_expense_cli(self):
        expense_id = int(questionary.text("Enter expense ID to update:").ask())
        amount = float(questionary.text("New amount:").ask())
        res = update_expense(UpdateExpense(expense_id=expense_id, amount=amount))
        print(res.message if res.success else res.error)

    def delete_expense_cli(self):
        expense_id = int(questionary.text("Enter expense ID to delete:").ask())
        res = delete_expense(expense_id)
        print(res.message if res.success else res.error)
