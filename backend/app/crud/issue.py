from app.crud.base import CRUDBase
from app.schemas.issue import IssueCreate, IssuePublic, IssueUpdate


class CRUDIssue(CRUDBase[IssueCreate, IssuePublic, IssueUpdate]):
    def create(self, create: IssueCreate) -> IssuePublic:
        pass

    def read(self, id: int) -> IssuePublic:
        pass

    def read_all(self) -> list[IssuePublic]:
        pass

    def update(self, id: int, update: IssueUpdate) -> IssuePublic:
        pass

    def delete(self, id: int):
        pass
