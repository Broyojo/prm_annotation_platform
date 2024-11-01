from app.crud.base import CRUDBase
from app.schemas.dataset import DatasetCreate, DatasetPublic, DatasetUpdate


class CRUDDataset(CRUDBase[DatasetCreate, DatasetPublic, DatasetUpdate]):
    def create(self, create: DatasetCreate) -> DatasetPublic:
        pass

    def read(self, id: int) -> DatasetPublic:
        pass

    def read_all(self) -> list[DatasetPublic]:
        pass

    def update(self, id: int, update: DatasetUpdate) -> DatasetPublic:
        pass

    def delete(self, id: int):
        pass
