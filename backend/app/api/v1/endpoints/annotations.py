from app.api.dependencies import get_api_user, get_session
from app.crud.annotation import CRUDAnnotation
from app.models.user import User
from app.schemas.annotation import AnnotationCreate, AnnotationPublic, AnnotationUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=AnnotationPublic)
def create_annotation(
    *,
    annotation_create: AnnotationCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationPublic:
    annotation = CRUDAnnotation(session).create(annotation_create)
    return annotation


@router.get("/", response_model=list[AnnotationPublic])
def read_annotations(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[AnnotationPublic]:
    annotations = CRUDAnnotation(session).read_all()
    return annotations


@router.get("/{annotation_id}", response_model=AnnotationPublic)
def read_annotation(
    *,
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationPublic:
    annotation = CRUDAnnotation(session).read(annotation_id)
    return annotation


@router.patch("/{annotation_id}", response_model=AnnotationPublic)
def update_annotation(
    *,
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationPublic:
    annotation = CRUDAnnotation(session).update(annotation_id, annotation_update)
    return annotation


@router.delete("/{annotation_id}")
def delete_annotation(
    *,
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
):
    CRUDAnnotation(session).delete(annotation_id)
