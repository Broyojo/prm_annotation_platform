from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_api_user, get_session
from app.crud.issue import CRUDIssue
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueRead, IssueUpdate

router = APIRouter()


@router.post("/", response_model=IssueRead)
def create_issue(
    *,
    issue_create: IssueCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> IssueRead:
    return CRUDIssue(session, api_user).create(issue_create)


@router.get("/", response_model=list[IssueRead])
def read_issues(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[IssueRead]:
    return CRUDIssue(session, api_user).read_all()


@router.get("/{issue_id}", response_model=IssueRead)
def read_issue(
    *,
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> IssueRead:
    return CRUDIssue(session, api_user).read(issue_id)


@router.patch("/{issue_id}", response_model=IssueRead)
def update_issue(
    *,
    issue_id: int,
    issue_update: IssueUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> IssueRead:
    return CRUDIssue(session, api_user).update(issue_id, issue_update)


@router.delete("/{issue_id}", response_model=IssueRead)
def delete_issue(
    *,
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> IssueRead:
    return CRUDIssue(session, api_user).delete(issue_id)
