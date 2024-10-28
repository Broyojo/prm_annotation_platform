from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/problems", tags=["Problems"])
from models import Annotation, Issue, Problem, ProblemPublic


@router.get("/", response_model=list[ProblemPublic])
async def read_problems(session: Session = Depends(get_session)):
    problems = session.exec(select(Problem)).all()
    return problems


@router.get("/{problem_id}", response_model=ProblemPublic)
async def read_problem(problem_id: int, session: Session = Depends(get_session)):
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/{problem_id}/annotations")
async def read_problem_annotations(
    problem_id: int, session: Session = Depends(get_session)
):
    if not session.get(Problem, problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    query = select(Annotation).where(Annotation.problem_id == problem_id)
    annotations = session.exec(query).all()
    return annotations


@router.get("/{problem_id}/issues")
async def read_problem_issues(problem_id: int, session: Session = Depends(get_session)):
    if not session.get(Problem, problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    query = select(Issue).where(Issue.problem_id == problem_id)
    annotations = session.exec(query).all()
    return annotations
