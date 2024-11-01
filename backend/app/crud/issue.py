from app.crud.base import CRUDBase
from app.schemas.issue import IssueCreate, IssuePublic, IssueUpdate


class CRUDIssue(CRUDBase[IssueCreate, IssuePublic, IssueUpdate]):
    def create(self, create: IssueCreate) -> IssueCreate:
        pass

    def read(self, id: int) -> IssueCreate:
        pass

    def read_all(self) -> list[IssueCreate]:
        pass

    def update(self, id: int, update: IssueUpdate) -> IssueCreate:
        pass

    def delete(self, id: int):
        pass
