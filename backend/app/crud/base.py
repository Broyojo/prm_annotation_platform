from sqlmodel import Session

from app.models.user import User


class CRUDBase:
    def __init__(self, session: Session, api_user: User):
        self.session = session
        self.api_user = api_user
