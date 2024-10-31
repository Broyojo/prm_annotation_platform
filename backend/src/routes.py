from datetime import datetime

from auth import authenticate_user
from database import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    Annotation,
    AnnotationCreate,
    AnnotationPublic,
    Dataset,
    DatasetCreate,
    DatasetPublic,
    Issue,
    IssueCreate,
    IssuePublic,
    Problem,
    ProblemCreate,
    ProblemPublic,
    User,
    UserCreate,
    UserPublic,
    UserUpdate,
)
from sqlmodel import Session, select

router = APIRouter()


@router.get("/users", response_model=list[UserPublic], tags=["Users"])
async def read_users(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[UserPublic]:
    return [
        (
            UserPublic.model_validate(user)
            if api_user.permissions == "admin" or api_user.id == user.id
            else UserPublic.model_validate(
                {
                    **user.model_dump(),
                    "api_key": (
                        ""
                        if (api_user.permissions != "admin" and api_user.id != user.id)
                        else user.api_key
                    ),
                }
            )
        )
        for user in session.exec(select(User))
    ]


@router.post("/users", response_model=UserPublic, tags=["Users"])
async def create_user(
    user_create: UserCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> UserPublic:
    if api_user.permissions != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non-admin user cannot create user",
        )

    db_user = user_create.to_db_model()

    try:
        session.add(db_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    session.refresh(db_user)
    return UserPublic.model_validate(db_user)


@router.get("/users/{user_id}", response_model=UserPublic, tags=["Users"])
async def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> UserPublic:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return (
        UserPublic.model_validate(user)
        if api_user.permissions == "admin" or api_user.id == user
        else UserPublic.model_validate(
            {
                **user.model_dump(),
                "api_key": (
                    ""
                    if (api_user.permissions != "admin" and api_user.id != user.id)
                    else user.api_key
                ),
            }
        )
    )


@router.patch("/users/{user_id}", response_model=UserPublic, tags=["Users"])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> UserPublic:
    if api_user.permissions != "admin" and api_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non-admin user cannot update user other than themselves",
        )

    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        db_user.sqlmodel_update(user_update)
        db_user.last_modified = datetime.now()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    session.refresh(db_user)
    return UserPublic.model_validate(db_user)


@router.delete("/users/{user_id}", tags=["Users"])
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if api_user.permissions != "admin" and api_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non-admin user cannot delete users other than themselves",
        )

    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        session.delete(db_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


@router.get(
    "/users/{user_id}/problems", response_model=list[ProblemPublic], tags=["Users"]
)
async def read_user_problems(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[ProblemPublic]:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    problems = [
        ProblemPublic.model_validate(problem)
        for problem in session.exec(
            select(Problem).where(Problem.creator_id == user_id)
        )
    ]
    return problems


@router.get(
    "/users/{user_id}/annotations",
    response_model=list[AnnotationPublic],
    tags=["Users"],
)
async def read_user_annotations(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[AnnotationPublic]:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    annotations = [
        AnnotationPublic.model_validate(annotation)
        for annotation in session.exec(
            select(Annotation).where(Annotation.creator_id == user_id)
        )
    ]
    return annotations


@router.get("/users/{user_id}/issues", response_model=list[IssuePublic], tags=["Users"])
async def read_user_issues(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[IssuePublic]:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    issues = [
        IssuePublic.model_validate(issue)
        for issue in session.exec(select(Issue).where(Issue.creator_id == user_id))
    ]
    return issues


@router.get("/datasets", response_model=list[DatasetPublic], tags=["Datasets"])
async def read_datasets(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[DatasetPublic]:
    return [
        DatasetPublic.model_validate(dataset)
        for dataset in session.exec(select(Dataset))
    ]


@router.post("/datasets", response_model=DatasetPublic, tags=["Datasets"])
async def create_dataset(
    dataset: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    db_dataset = dataset.to_db_model(creator_id=api_user.id)

    try:
        session.add(db_dataset)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    session.refresh(db_dataset)
    return DatasetPublic.model_validate(db_dataset)


@router.get("/datasets/{dataset_id}", response_model=DatasetPublic, tags=["Datasets"])
async def read_dataset(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    dataset = session.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )
    return DatasetPublic.model_validate(dataset)


@router.patch("/datasets/{dataset_id}", response_model=DatasetPublic, tags=["Datasets"])
async def update_dataset(
    dataset_id: int,
    dataset: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    pass


@router.delete("/datasets/{dataset_id}", tags=["Datasets"])
async def delete_dataset(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get(
    "/datasets/{dataset_id}/problems",
    response_model=list[ProblemPublic],
    tags=["Datasets"],
)
async def read_dataset_problems(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[ProblemPublic]:
    if session.get(Dataset, dataset_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )
    query = select(Problem).where(Problem.dataset_id == dataset_id)
    problems = [
        ProblemPublic.model_validate(problem) for problem in session.exec(query)
    ]
    return problems


@router.get(
    "/datasets/{dataset_id}/annotations",
    response_model=list[AnnotationPublic],
    tags=["Datasets"],
)
async def read_dataset_annotations(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[AnnotationPublic]:
    pass


@router.get(
    "/datasets/{dataset_id}/issues", response_model=list[IssuePublic], tags=["Datasets"]
)
async def read_dataset_issues(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[IssuePublic]:
    pass


@router.get("/problems", response_model=list[ProblemPublic], tags=["Problems"])
async def read_problems(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[ProblemPublic]:
    return [
        ProblemPublic.model_validate(problem)
        for problem in session.exec(select(Problem))
    ]


@router.post("/problems", response_model=ProblemPublic, tags=["Problems"])
async def create_problem(
    problem: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> ProblemPublic:
    pass


@router.get("/problems/{problem_id}", response_model=ProblemPublic, tags=["Problems"])
async def read_problem(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> ProblemPublic:
    problem = session.get(Problem, problem_id)
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )
    return ProblemPublic.model_validate(problem)


@router.patch("/problems/{problem_id}", response_model=ProblemPublic, tags=["Problems"])
async def update_problem(
    problem_id: int,
    problem: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> ProblemPublic:
    pass


@router.delete("/problems/{problem_id}", tags=["Problems"])
async def delete_problem(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get(
    "/problems/{problem_id}/annotations",
    response_model=list[AnnotationPublic],
    tags=["Problems"],
)
async def read_problem_annotations(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[AnnotationPublic]:
    if session.get(Problem, problem_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )
    query = select(Annotation).where(Annotation.problem_id == problem_id)
    annotations = [
        AnnotationPublic.model_validate(annotation)
        for annotation in session.exec(query)
    ]
    return annotations


@router.get(
    "/problems/{problem_id}/issues", response_model=list[IssuePublic], tags=["Problems"]
)
async def read_problem_issues(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[IssuePublic]:
    if session.get(Problem, problem_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )
    query = select(Issue).where(Issue.problem_id == problem_id)
    annotations = [IssuePublic.model_validate(issue) for issue in session.exec(query)]
    return annotations


@router.get("/annotations", response_model=list[AnnotationPublic], tags=["Annotations"])
async def read_annotations(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[AnnotationPublic]:
    return [
        AnnotationPublic.model_validate(annotation)
        for annotation in session.exec(select(Annotation))
    ]


@router.post("/annotations", response_model=AnnotationPublic, tags=["Annotations"])
async def create_annotation(
    annotation: AnnotationCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> AnnotationPublic:
    pass


@router.get(
    "/annotations/{annotation_id}",
    response_model=AnnotationPublic,
    tags=["Annotations"],
)
async def read_annotation(
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> AnnotationPublic:
    annotation = session.get(Annotation, annotation_id)
    if annotation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found"
        )
    return AnnotationPublic.model_validate(annotation)


@router.patch(
    "/annotations/{annotation_id}",
    response_model=AnnotationPublic,
    tags=["Annotations"],
)
async def update_annotation(
    annotation_id: int,
    annotation: AnnotationCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> AnnotationPublic:
    pass


@router.delete("/annotations/{annotation_id}", tags=["Annotations"])
async def delete_annotation(
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get("/issues", response_model=list[IssuePublic], tags=["Issues"])
async def read_issues(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> list[IssuePublic]:
    return [IssuePublic.model_validate(issue) for issue in session.exec(select(Issue))]


@router.post("/issues", response_model=IssuePublic, tags=["Issues"])
async def create_issue(
    issue: IssueCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> IssuePublic:
    pass


@router.get("/issues/{issue_id}", response_model=IssuePublic, tags=["Issues"])
async def read_issue(
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> IssuePublic:
    issue = session.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )
    return IssuePublic.model_validate(issue)


@router.patch("/issues/{issue_id}", response_model=IssuePublic, tags=["Issues"])
async def update_issue(
    issue_id: int,
    issue: IssueCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> IssuePublic:
    pass


@router.delete("/issues/{issue_id}", tags=["Issues"])
async def delete_issue(
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass
