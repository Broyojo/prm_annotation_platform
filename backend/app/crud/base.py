from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.schemas.base import CreateBase, PublicBase, UpdateBase
from sqlmodel import Session

CreateSchemaType = TypeVar("CreateSchemaType", bound=CreateBase)
PublicSchemaType = TypeVar("PublicSchemaType", bound=PublicBase)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UpdateBase)


class CRUDBase(Generic[CreateSchemaType, PublicSchemaType, UpdateSchemaType], ABC):
    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def create(self, id: int, create: CreateSchemaType) -> PublicSchemaType:
        pass

    @abstractmethod
    def read(self, id: int) -> PublicSchemaType:
        pass

    @abstractmethod
    def read_all(self) -> list[PublicSchemaType]:
        pass

    @abstractmethod
    def update(self, id: int, update: UpdateSchemaType) -> PublicSchemaType:
        pass
