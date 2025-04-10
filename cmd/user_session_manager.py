import json
from schema.schema import User
from api.auth import auth
from pydantic import BaseModel
from typing import Optional
from pprint import pprint


class CurrentUserData(BaseModel):
    user_id: int = 0
    username: str = ""
    email: str = ""


class UserSession(BaseModel):
    cookie: Optional[str] = ""
    has_logged_in: bool = False
    previous_username: str = ""
    current_user_data: CurrentUserData = CurrentUserData()


class UserSessionManager:
    def __init__(self, save_file="./cmd/save_data.json"):
        self.save_file = save_file
        self.user_session = UserSession()
        self.current_user: User = None

    def sync_user_session(self):
        try:
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.user_session = UserSession(**data)

                if not self.user_session.has_logged_in:
                    return

                result = auth(jwt=self.user_session.cookie)
                if result.success:
                    self.current_user = result.result.user
                else:
                    print("Authentication failed. Please log in again.")
                    self.reset_session()
        except Exception as e:
            print(f"Error loading save data: {e}")

    def save_user_session(self):
        try:
            with open(self.save_file, "w") as f:
                pprint(self.user_session)
                json.dump(self.user_session.model_dump(), f, indent=4)
        except Exception as e:
            print(f"Error saving session: {e}")

    def reset_session(self):
        self.user_session = UserSession()
        self.current_user = None
        self.save_user_session()
