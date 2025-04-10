from api.incomes import create_income, read_income_list, update_income, delete_income
from schema.schema import CreateIncome, UpdateIncome
import questionary
from pprint import pprint


class IncomeCLI:
    def __init__(self, session_manager):
        self.session = session_manager

    def income_menu(self):
        while True:
            action = questionary.select(
                "Income Menu",
                choices=["Add Income", "View Income", "Update Income", "Delete Income"],
            ).ask(kbi_msg="Exited income menu.")

            if not action:
                break

            getattr(self, action.lower().replace(" ", "_") + "_cli")()

    def add_income_cli(self):
        amount = float(questionary.text("Enter income amount:").ask())
        description = questionary.text("Description about income:").ask()
        income_date = questionary.text("Income Date (YYYY-MM-DD):").ask()

        res = create_income(
            CreateIncome(
                user_id=self.session.current_user.user_id,
                amount=amount,
                description=description,
                income_date=income_date,
            )
        )
        print(res.message if res.success else res.error)

    def view_income_cli(self):
        res = read_income_list(self.session.current_user.user_id)
        pprint(res.result if res.success else res.error)

    def update_income_cli(self):
        income_id = int(questionary.text("Enter income ID to update:").ask())
        amount = float(questionary.text("New amount:").ask())
        res = update_income(UpdateIncome(income_id=income_id, amount=amount))
        print(res.message if res.success else res.error)

    def delete_income_cli(self):
        income_id = int(questionary.text("Enter income ID to delete:").ask())
        res = delete_income(income_id)
        print(res.message if res.success else res.error)
