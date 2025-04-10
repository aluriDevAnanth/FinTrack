from pprint import pprint
import questionary
from api.transactions import read_transaction_list


class TransactionsCLI:
    def __init__(self, session_manager):
        self.session = session_manager

    def transactions_menu(self):
        while True:
            action = questionary.select(
                "Transactions Menu", choices=["View All Transactions"]
            ).ask(kbi_msg="Exited transactions menu.")

            if not action:
                break

            self.view_transactions_cli()

    def view_transactions_cli(self):
        res = read_transaction_list(self.session.current_user.user_id)
        pprint(res.result if res.success else res.error)
