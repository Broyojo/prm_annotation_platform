from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select

from app.crud.base import CRUDBase
from app.crud.problem import CRUDProblem
from app.models.annotation import Annotation
from app.schemas.annotation import AnnotationCreate, AnnotationRead, AnnotationUpdate


class CRUDAnnotation(CRUDBase):
    def create(self, annotation_create: AnnotationCreate) -> AnnotationRead:
        db_annotation = Annotation(
            **annotation_create.model_dump(), creator_id=self.api_user.id
        )

        CRUDProblem(self.session, self.api_user).read(annotation_create.problem_id)

        try:
            self.session.add(db_annotation)
            self.session.commit()
            self.session.refresh(db_annotation)
            return AnnotationRead.model_validate(db_annotation)
        except Exception as e:
            self.session.rollback()
            raise e

    def read_db_annotation(self, annotation_id) -> Annotation:
        db_annotation = self.session.get(Annotation, annotation_id)
        if db_annotation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation with id {annotation_id} not found",
            )
        return db_annotation

    def read(self, annotation_id: int) -> AnnotationRead:
        db_annotation = self.read_db_annotation(annotation_id)
        return AnnotationRead.model_validate(db_annotation)

    def read_all(self) -> list[AnnotationRead]:
        db_annotations = self.session.exec(select(Annotation)).all()
        return [
            AnnotationRead.model_validate(annotation) for annotation in db_annotations
        ]

    def update(
        self, annotation_id: int, annotation_update: AnnotationUpdate
    ) -> AnnotationRead:
        db_annotation = self.read_db_annotation(annotation_id)
        try:
            db_annotation = db_annotation.sqlmodel_update(
                annotation_update.model_dump(exclude_unset=True)
            )
            db_annotation.last_modified = datetime.now()
            self.session.add(db_annotation)
            self.session.commit()
            self.session.refresh(db_annotation)
            return AnnotationRead.model_validate(db_annotation)
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, annotation_id) -> AnnotationRead:
        db_annotation = self.read_db_annotation(annotation_id)
        try:
            self.session.delete(db_annotation)
            self.session.commit()
            return AnnotationRead.model_validate(db_annotation)
        except Exception as e:
            self.session.rollback()
            raise e
