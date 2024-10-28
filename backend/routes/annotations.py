from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/annotations", tags=["Annotations"])
from models import Annotation, AnnotationPublic


@router.get("/", response_model=list[AnnotationPublic])
async def read_annotations(session: Session = Depends(get_session)):
    return session.exec(select(Annotation)).all()


@router.get("/{annotation_id}", response_model=AnnotationPublic)
async def read_annotation(annotation_id: int, session: Session = Depends(get_session)):
    annotation = session.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation
