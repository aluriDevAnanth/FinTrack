from decimal import Decimal
from pprint import pprint
import questionary
from colorama import init, Fore, Style
from py_backend.api.transactions import (
    read_transaction_list,
    create_transaction,
    update_transaction,
    delete_transaction,
)
from schema.schema import CreateTransaction, UpdateTransaction, TransactionType
from cli.user_session_manager import UserSessionManager
from datetime import date

init(autoreset=True)


class TransactionsCLI:
    def __init__(self, session_manager: UserSessionManager):
        self.session = session_manager

    def transactions_menu(self):
        while True:
            try:
                action = questionary.select(
                    "Transactions Menu",
                    choices=[
                        "Add Transaction",
                        "View Transactions",
                        "Update Transaction",
                        "Delete Transaction",
                    ],
                ).ask(kbi_msg="Exited transactions menu.")

                if not action:
                    break

                if self.session.current_user is None:
                    self.session.login_or_create_account()
                    break

                getattr(self, action.lower().replace(" ", "_") + "_cli")()
            except Exception as e:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + f"[Exception in transactions_menu] {type(e).__name__}: {str(e)}"
                )

    def add_transaction_cli(self):
        try:
            amount = float(questionary.text("Enter transaction amount: ").ask())
            description = questionary.text("Enter Description: ").ask()
            transaction_date = questionary.text("Enter Date (YYYY-MM-DD): ").ask()
            transaction_date = (
                date.today() if transaction_date == "" else transaction_date
            )
            typee = questionary.select(
                "Choose Type: ", choices=["income", "expense"]
            ).ask()

            res = create_transaction(
                CreateTransaction(
                    user_id=self.session.current_user.user_id,
                    amount=amount,
                    description=description,
                    transaction_date=transaction_date,
                    type=typee,
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
                + f"[Exception in add_transaction_cli] {type(e).__name__}: {str(e)}"
            )

    def view_transactions_cli(self):
        try:
            res = read_transaction_list(self.session.current_user.user_id)
            pprint(
                [i.model_dump() for i in res.result]
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in view_transactions_cli] {type(e).__name__}: {str(e)}"
            )

    def update_transaction_cli(self):
        try:
            transaction_id_input = questionary.text(
                "Enter transaction ID to update:"
            ).ask()
            if not transaction_id_input:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + "Exited update transaction as transaction_id is mandatory field."
                )
                return

            transaction_id = int(transaction_id_input)
            update_data = UpdateTransaction(
                transaction_id=transaction_id,
                user_id=self.session.current_user.user_id,
            )

            amount_input = questionary.text("New amount:").ask()
            if amount_input:
                update_data.amount = Decimal(amount_input)

            description = questionary.text("New description:").ask()
            if description:
                update_data.description = description

            transaction_date = questionary.text(
                "New transaction date (YYYY-MM-DD): "
            ).ask()
            if transaction_date:
                update_data.transaction_date = transaction_date

            typee = questionary.checkbox(
                "New Type:", choices=["income", "expense"]
            ).ask()
            if typee and len(typee) == 1:
                update_data.type = typee[0]
            elif typee and len(typee) != 1:
                while True:
                    print(Fore.RED + Style.BRIGHT + "Please select only one type.")
                    typee = questionary.checkbox(
                        "New Type:", choices=["income", "expense"]
                    ).ask()
                    if typee and len(typee) == 1:
                        update_data.type = typee[0]
                        break

            res = update_transaction(update_data)
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in update_transaction_cli] {type(e).__name__}: {str(e)}"
            )

    def delete_transaction_cli(self):
        try:
            transaction_id_input = questionary.text(
                "Enter transaction ID to delete:"
            ).ask()
            transaction_id = int(transaction_id_input)

            res = delete_transaction(transaction_id, self.session.current_user.user_id)
            print(
                res.message
                if res.success
                else Fore.RED + Style.BRIGHT + f"{res.errorType}: {res.error}"
            )
        except Exception as e:
            print(
                Fore.RED
                + Style.BRIGHT
                + f"[Exception in delete_transaction_cli] {type(e).__name__}: {str(e)}"
            )
