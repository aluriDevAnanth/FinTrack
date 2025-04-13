from decimal import Decimal
from py_backend.api.savings_goals import (
    create_savings_goal,
    read_savings_goals,
    update_savings_goal,
    delete_savings_goal,
)
from schema.schema import CreateSavingsGoal, UpdateSavingsGoal
from datetime import date
from pprint import pprint
from colorama import init, Fore, Style
import questionary
from cli.user_session_manager import UserSessionManager


init(autoreset=True)


class SavingsGoalsCLI:

    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def savings_goals_menu(self):
        while True:
            try:
                action = questionary.select(
                    "Savings Goals Menu",
                    choices=["Create Goal", "View Goals", "Update Goal", "Delete Goal"],
                ).ask(kbi_msg="Exited savings goals menu.")

                if not action:
                    break

                getattr(self, action.lower().replace(" ", "_") + "_cli")()
            except Exception as e:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + f"[Exception in savings_goals_menu] {type(e).__name__}: {str(e)}"
                )

    def create_goal_cli(self):
        try:
            name = questionary.text("Enter Goal Name:").ask()
            target_amount = Decimal(questionary.text("Enter Target Amount:").ask())
            current_amount = Decimal(questionary.text("Enter Current Amount:").ask())
            target_date = questionary.text("Enter Target Date (YYYY-MM-DD):").ask()

            res = create_savings_goal(
                CreateSavingsGoal(
                    user_id=self.session.current_user.user_id,
                    name=name,
                    target_amount=target_amount,
                    current_amount=current_amount,
                    target_date=(
                        date.fromisoformat(target_date) if target_date else date.today()
                    ),
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
                + f"[Exception in create_goal_cli] {type(e).__name__}: {str(e)}"
            )

    def view_goals_cli(self):
        try:
            res = read_savings_goals(self.session.current_user.user_id)
            (
                pprint([i.model_dump() for i in res.result])
                if res.success
                else print(Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}")
            )

        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in view_goals_cli] {type(e).__name__}: {str(e)}"
            )

    def update_goal_cli(self):
        try:
            goal_id = int(questionary.text("Enter goal ID to update:").ask(kbi_msg=""))
            goal_data = UpdateSavingsGoal(
                goal_id=goal_id, user_id=self.session.current_user.user_id
            )

            name = questionary.text("Enter New goal Name: ").ask(kbi_msg="")
            if name:
                goal_data.name = name

            target_amount = questionary.text("Enter New Target Amount:").ask(kbi_msg="")
            if target_amount:
                goal_data.target_amount = Decimal(target_amount)

            current_amount = questionary.text("Enter New Current Amount saved:").ask(
                kbi_msg=""
            )
            if current_amount:
                goal_data.current_amount = Decimal(current_amount)

            target_date = questionary.text("Enter New Target Date (YYYY-MM-DD):").ask(
                kbi_msg=""
            )
            if target_date:
                goal_data.target_date = date.fromisoformat(target_date)

            if not questionary.confirm(
                "Confirm to Update: " + repr(goal_data), default=False
            ).ask():
                return

            res = update_savings_goal(goal_data)
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except KeyboardInterrupt as e:
            return
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in update_goal_cli] {type(e).__name__}: {str(e)}"
            )

    def delete_goal_cli(self):
        try:
            goal_id = int(questionary.text("Enter goal ID to delete:").ask())
            res = delete_savings_goal(goal_id)
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in delete_goal_cli] {type(e).__name__}: {str(e)}"
            )
