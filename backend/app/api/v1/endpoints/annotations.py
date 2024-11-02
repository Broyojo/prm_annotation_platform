from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_api_user, get_session
from app.crud.annotation import CRUDAnnotation
from app.models.user import User
from app.schemas.annotation import AnnotationCreate, AnnotationRead, AnnotationUpdate

router = APIRouter()


@router.post("/", response_model=AnnotationRead)
def create_annotation(
    *,
    annotation_create: AnnotationCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationRead:
    return CRUDAnnotation(session, api_user).create(annotation_create)


@router.get("/", response_model=list[AnnotationRead])
def read_annotations(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[AnnotationRead]:
    return CRUDAnnotation(session, api_user).read_all()


@router.get("/{annotation_id}", response_model=AnnotationRead)
def read_annotation(
    *,
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationRead:
    return CRUDAnnotation(session, api_user).read(annotation_id)


@router.patch("/{annotation_id}", response_model=AnnotationRead)
def update_annotation(
    *,
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationRead:
    return CRUDAnnotation(session, api_user).update(annotation_id, annotation_update)


@router.delete("/{annotation_id}", response_model=AnnotationRead)
def delete_annotation(
    *,
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> AnnotationRead:
    return CRUDAnnotation(session, api_user).delete(annotation_id)
