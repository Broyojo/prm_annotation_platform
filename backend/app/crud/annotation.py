from app.crud.base import CRUDBase
from app.schemas.annotation import AnnotationCreate, AnnotationPublic, AnnotationUpdate


class CRUDAnnotation(CRUDBase[AnnotationCreate, AnnotationPublic, AnnotationUpdate]):
    def create(self, create: AnnotationCreate) -> AnnotationPublic:
        pass

    def read(self, id: int) -> AnnotationPublic:
        pass

    def read_all(self) -> list[AnnotationPublic]:
        pass

    def update(self, id: int, update: AnnotationUpdate) -> AnnotationPublic:
        pass

    def delete(self, id: int):
        pass
