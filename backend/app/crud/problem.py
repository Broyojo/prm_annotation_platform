from app.crud.base import CRUDBase
from app.schemas.problem import ProblemCreate, ProblemPublic, ProblemUpdate


class CRUDProblem(CRUDBase[ProblemCreate, ProblemPublic, ProblemUpdate]):
    def create(self, create: ProblemCreate) -> ProblemPublic:
        pass

    def read(self, id: int) -> ProblemPublic:
        pass

    def read_all(self) -> list[ProblemPublic]:
        pass

    def update(self, id: int, update: ProblemUpdate) -> ProblemPublic:
        pass

    def delete(self, id: int):
        pass
