from app.crud.base import CRUDBase
from app.schemas.user import UserCreate, UserPublic, UserUpdate


class CRUDUser(CRUDBase[UserCreate, UserPublic, UserUpdate]):
    def create(self, create: UserCreate) -> UserPublic:
        pass

    def read(self, id: int) -> UserPublic:
        pass

    def read_all(self) -> list[UserPublic]:
        pass

    def update(self, id: int, update: UserUpdate) -> UserPublic:
        pass

    def delete(self, id: int):
        pass
