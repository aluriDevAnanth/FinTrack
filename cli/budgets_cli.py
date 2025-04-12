from datetime import date, timedelta
from pprint import pprint
import questionary
from colorama import init, Fore, Style
from py_backend.api.budgets import (
    create_budget,
    read_budget_list,
    update_budget,
    delete_budget,
)
from schema.schema import CreateBudget, UpdateBudget
from decimal import Decimal
from cli.user_session_manager import UserSessionManager

init(autoreset=True)


class BudgetsCLI:

    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def budgets_menu(self):
        while True:
            try:
                action = questionary.select(
                    "Budgets Menu",
                    choices=[
                        "Create Budget",
                        "View Budgets",
                        "Update Budget",
                        "Delete Budget",
                    ],
                ).ask(kbi_msg="Exited budgets menu.")

                if not action:
                    break

                getattr(self, action.lower().replace(" ", "_") + "_cli")()
            except Exception as e:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + f"[Exception in budgets_menu] {type(e).__name__}: {str(e)}"
                )

    def create_budget_cli(self):
        try:
            amount = Decimal(questionary.text("Enter amount:").ask())

            while True:
                start_date = questionary.text("Enter start_date: (YYYY-MM-DD)").ask()
                start_date = (
                    date.today() if start_date == "" else date.fromisoformat(start_date)
                )
                end_date = questionary.text("Enter end_date: (YYYY-MM-DD)").ask()
                end_date = (
                    timedelta(30) + date.today()
                    if end_date == ""
                    else date.fromisoformat(end_date)
                )

                if start_date < date.today():
                    print(
                        Fore.RED
                        + Style.BRIGHT
                        + "Start date must be today or in the future."
                    )
                    continue

                if end_date <= date.today():
                    print(Fore.RED + Style.BRIGHT + "End date must be after today.")
                    continue

                if end_date <= start_date:
                    print(
                        Fore.RED + Style.BRIGHT + "End date must be after start date."
                    )
                    continue

                break

            res = create_budget(
                CreateBudget(
                    user_id=self.session.current_user.user_id,
                    amount=amount,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in create_budget_cli] {type(e).__name__}: {str(e)}"
            )

    def view_budgets_cli(self):
        try:
            res = read_budget_list(self.session.current_user.user_id)
            pprint(
                [i.model_dump() for i in res.result]
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in view_budgets_cli] {type(e).__name__}: {str(e)}"
            )

    def update_budget_cli(self):
        try:
            budget_id = int(questionary.text("Enter budget ID to update:").ask())
            update_budget_data = UpdateBudget(
                budget_id=budget_id, user_id=self.session.current_user.user_id
            )
            amount = questionary.text("Enter amount:").ask()
            if amount:
                update_budget_data.amount = Decimal(amount)

            while True:
                start_date = questionary.text("Enter start_date: (YYYY-MM-DD)").ask()
                start_date = (
                    date.today() if start_date == "" else date.fromisoformat(start_date)
                )
                end_date = questionary.text("Enter end_date: (YYYY-MM-DD)").ask()
                end_date = (
                    timedelta(30) + date.today()
                    if end_date == ""
                    else date.fromisoformat(end_date)
                )

                if start_date < date.today():
                    print(
                        Fore.RED
                        + Style.BRIGHT
                        + "Start date must be today or in the future."
                    )
                    continue

                if end_date <= date.today():
                    print(Fore.RED + Style.BRIGHT + "End date must be after today.")
                    continue

                if end_date <= start_date:
                    print(
                        Fore.RED + Style.BRIGHT + "End date must be after start date."
                    )
                    continue

                update_budget_data.start_date = start_date
                update_budget_data.end_date = end_date
                break

            res = update_budget(update_budget_data)
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in update_budget_cli] {type(e).__name__}: {str(e)}"
            )

    def delete_budget_cli(self):
        try:
            budget_id = int(questionary.text("Enter budget ID to delete:").ask())
            res = delete_budget(budget_id)
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in delete_budget_cli] {type(e).__name__}: {str(e)}"
            )
