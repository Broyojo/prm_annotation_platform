from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_api_user, get_session
from app.crud.problem import CRUDProblem
from app.models.user import User
from app.schemas.annotation import AnnotationRead
from app.schemas.issue import IssueRead
from app.schemas.problem import ProblemCreate, ProblemRead, ProblemUpdate

router = APIRouter()


@router.post("/", response_model=ProblemRead)
def create_problem(
    *,
    problem_create: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemRead:
    return CRUDProblem(session, api_user).create(problem_create)


@router.get("/", response_model=list[ProblemRead])
def read_problems(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[ProblemRead]:
    return CRUDProblem(session, api_user).read_all()


@router.get("/{problem_id}", response_model=ProblemRead)
def read_problem(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemRead:
    return CRUDProblem(session, api_user).read(problem_id)


@router.get("/{problem_id}/annotations", response_model=list[AnnotationRead])
def read_problem_annotations(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[AnnotationRead]:
    return CRUDProblem(session, api_user).read_problem_annotations(problem_id)


@router.get("/{problem_id}/issues", response_model=list[IssueRead])
def read_problem_issues(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[IssueRead]:
    return CRUDProblem(session, api_user).read_problem_issues(problem_id)


@router.patch("/{problem_id}", response_model=ProblemRead)
def update_problem(
    *,
    problem_id: int,
    problem_update: ProblemUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemRead:
    return CRUDProblem(session, api_user).update(problem_id, problem_update)


@router.delete("/{problem_id}", response_model=ProblemRead)
def delete_problem(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemRead:
    return CRUDProblem(session, api_user).delete(problem_id)
