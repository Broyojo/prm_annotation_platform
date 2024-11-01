from app.api.dependencies import get_api_user, get_session
from app.crud.problem import CRUDProblem
from app.models.user import User
from app.schemas.annotation import AnnotationPublic
from app.schemas.issue import IssuePublic
from app.schemas.problem import ProblemCreate, ProblemPublic, ProblemUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=ProblemPublic)
def create_problem(
    *,
    problem_create: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemPublic:
    problem = CRUDProblem(session).create(problem_create)
    return problem


@router.get("/", response_model=list[ProblemPublic])
def read_problems(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[ProblemPublic]:
    problems = CRUDProblem(session).read_all()
    return problems


@router.get("/{problem_id}", response_model=ProblemPublic)
def read_problem(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemPublic:
    problem = CRUDProblem(session).read(problem_id)
    return problem


@router.patch("/{problem_id}", response_model=ProblemPublic)
def update_problem(
    *,
    problem_id: int,
    problem_update: ProblemUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> ProblemPublic:
    problem = CRUDProblem(session).update(problem_id, problem_update)
    return problem


@router.delete("/{problem_id}")
def delete_problem(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
):
    CRUDProblem(session).delete(problem_id)


@router.get("/{problem_id}/annotations", response_model=list[AnnotationPublic])
def read_problem_annotations(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[AnnotationPublic]:
    pass


@router.get("/{problem_id}/issues", response_model=list[IssuePublic])
def read_problem_issues(
    *,
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[IssuePublic]:
    pass
