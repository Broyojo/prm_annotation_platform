from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/issues", tags=["Issues"])
from models import Issue, IssuePublic


@router.get("/", response_model=list[IssuePublic])
async def read_issues(session: Session = Depends(get_session)):
    return session.exec(select(Issue)).all()


@router.get("/{issue_id}", response_model=IssuePublic)
async def read_issue(issue_id: int, session: Session = Depends(get_session)):
    issue = session.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue
