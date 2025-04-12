from pprint import pprint
import questionary
from colorama import init, Fore, Style
from api.budgets import create_budget, read_budget_list, update_budget, delete_budget
from schema.schema import CreateBudget, UpdateBudget

init(autoreset=True)


class BudgetsCLI:
    def __init__(self, session_manager):
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
            category = questionary.text("Budget Category:").ask()
            limit = float(questionary.text("Budget Limit:").ask())
            res = create_budget(
                CreateBudget(
                    user_id=self.session.current_user.user_id,
                    category=category,
                    limit=limit,
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
            limit = float(questionary.text("New limit:").ask())
            res = update_budget(UpdateBudget(budget_id=budget_id, limit=limit))
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
