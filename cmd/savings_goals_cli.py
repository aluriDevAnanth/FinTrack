from api.savings_goals import (
    create_savings_goal,
    read_savings_goals,
    update_savings_goal,
    delete_savings_goal,
)
from schema.schema import CreateSavingsGoal, UpdateSavingsGoal
from datetime import date
from pprint import pprint
import questionary


class SavingsGoalsCLI:
    def __init__(self, session_manager):
        self.session = session_manager

    def savings_goals_menu(self):
        while True:
            action = questionary.select(
                "Savings Goals Menu",
                choices=["Create Goal", "View Goals", "Update Goal", "Delete Goal"],
            ).ask(kbi_msg="Exited savings goals menu.")

            if not action:
                break

            getattr(self, action.lower().replace(" ", "_") + "_cli")()

    def create_goal_cli(self):
        name = questionary.text("Goal Name:").ask()
        target_amount = float(questionary.text("Target Amount:").ask())
        target_date = questionary.text("Target Date (YYYY-MM-DD):").ask()

        res = create_savings_goal(
            CreateSavingsGoal(
                user_id=self.session.current_user.user_id,
                name=name,
                target_amount=target_amount,
                target_date=date.fromisoformat(target_date),
            )
        )
        print(res.message if res.success else res.error)

    def view_goals_cli(self):
        res = read_savings_goals(self.session.current_user.user_id)
        pprint(res.result if res.success else res.error)

    def update_goal_cli(self):
        goal_id = int(questionary.text("Enter goal ID to update:").ask())
        current_amount = float(questionary.text("Enter current amount saved:").ask())
        res = update_savings_goal(
            UpdateSavingsGoal(goal_id=goal_id, current_amount=current_amount)
        )
        print(res.message if res.success else res.error)

    def delete_goal_cli(self):
        goal_id = int(questionary.text("Enter goal ID to delete:").ask())
        res = delete_savings_goal(goal_id)
        print(res.message if res.success else res.error)
