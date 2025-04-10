from colorama import init, Fore, Style
from api.incomes import create_income, read_income_list, update_income, delete_income
from cli.user_session_manager import UserSessionManager
from schema.schema import CreateIncome, UpdateIncome
import questionary
from pprint import pprint
from decimal import Decimal

init(autoreset=True)


class IncomeCLI:

    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def income_menu(self):
        while True:
            action = questionary.select(
                "Income Menu",
                choices=["Add Income", "View Income", "Update Income", "Delete Income"],
            ).ask(kbi_msg="Exited income menu.")

            if self.session.current_user is None:
                print("Please log in to access this menu.")
                self.session.login_or_create_account()
                continue

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
        pprint([i.model_dump() for i in res.result] if res.success else res)

    from decimal import Decimal

    def update_income_cli(self):
        try:
            income_id = questionary.text(
                "Enter Income ID to update: (mandatory field)"
            ).ask()
            if not income_id:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + "Exited update income as income_id is mandatory field, so skipping this means no update will be done."
                )
                return

            update_income_data = UpdateIncome(income_id=int(income_id))

            # Amount
            try:
                amount_input = questionary.text(
                    "Enter New Amount (or press Ctrl+C to skip):"
                ).ask()
                if amount_input:
                    update_income_data.amount = Decimal(amount_input)
            except KeyboardInterrupt:
                pass  # Skip amount update

            # Description
            try:
                description = questionary.text(
                    "Enter New Description (or press Ctrl+C to skip):"
                ).ask()
                if description:
                    update_income_data.description = description
            except KeyboardInterrupt:
                pass

            # Income Date
            try:
                income_date = questionary.text(
                    "Enter New Date (YYYY-MM-DD) (or press Ctrl+C to skip):"
                ).ask()
                if income_date:
                    update_income_data.income_date = income_date
            except KeyboardInterrupt:
                pass

            # Call the update function
            res = update_income(update_income_data)
            print(res.message if res.success else f"{res.errorType}: {res.error}")

        except KeyboardInterrupt:
            print("\nUpdate cancelled.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_income_cli(self):
        income_id = int(questionary.text("Enter income ID to delete:").ask())
        res = delete_income(income_id)
        print(res.message if res.success else res.error)
