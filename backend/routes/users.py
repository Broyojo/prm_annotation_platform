from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/users", tags=["Users"])
from models import Annotation, AnnotationPublic, Issue, IssuePublic, User, UserPublic


@router.get("/", response_model=list[UserPublic])
async def read_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/annotations", response_model=list[AnnotationPublic])
async def read_user_annotations(user_id: int, session: Session = Depends(get_session)):
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    annotations = session.exec(
        select(Annotation).where(Annotation.creator_id == user_id)
    ).all()
    return annotations


@router.get("/{user_id}/issues", response_model=list[IssuePublic], tags=["Users"])
async def read_user_issues(user_id: int, session: Session = Depends(get_session)):
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    issues = session.exec(select(Issue).where(Issue.creator_id == user_id)).all()
    return issues
