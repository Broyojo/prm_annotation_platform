import os
from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin
    """
    access level:
    1. standard - can do everything other than delete (annotate, read from api, upload datasets with questions, etc)
    2. admin - can delete problems/datasets
    """
    # a user can have many annotations
    annotations: list["Annotation"] = Relationship(back_populates="user")


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    step_labels: str  # json list of label per step

    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="annotations")

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="annotations")


class Problem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    question: str
    answer: str
    llm_answer: str
    steps: str  # json list of steps
    num_steps: int
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[str] = None  # json string of final answer

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )
    dataset_id: Optional[int] = Field(default=None, foreign_key="dataset.id")
    dataset: "Dataset" = Relationship(back_populates="problems")


class Dataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str
    domain: str  # math, coding, agentic, etc.

    problems: list[Problem] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


if __name__ == "__main__":
    import json
    import random
    import secrets

    WRITE = False

    if WRITE:
        from faker import Faker

        faker = Faker()

        users = []
        for _ in range(10):
            user = User(
                name=faker.name(),
                api_key=secrets.token_urlsafe(32),
                permissions="standard",
            )
            users.append(user)

        users.append(
            User(
                name="David Andrews",
                api_key=secrets.token_urlsafe(32),
                permissions="admin",
            )
        )

        print("Users:")
        for user in users:
            print(user)
        print()

        datasets = []
        for file in os.listdir("./test_data/normalized"):
            path = os.path.join("./test_data/normalized", file)
            dataset = Dataset(
                name=file.split(".")[0]
                .replace("_", " ")
                .replace("selected", "")
                .strip()
                .title(),
                domain="math",
            )

            with open(path, "r") as f:
                problems = json.load(f)

            for problem in problems:
                dataset.problems.append(
                    Problem(
                        question=problem["question"],
                        answer=problem["answer"],
                        llm_answer=problem["llm_answer"],
                        steps=json.dumps(problem["steps"]),
                        num_steps=problem["num_steps"],
                        is_correct=problem.get("is_correct"),
                        solve_ratio=problem.get("solve_ratio"),
                        llm_name=problem.get("llm_name"),
                        prompt_format=problem.get("prompt_format"),
                        final_answer=json.dumps(problem.get("final_answer")),
                    )
                )

            datasets.append(dataset)

        print("Datasets:")
        for dataset in datasets:
            print(dataset)
            print("Num problems:", len(dataset.problems))
        print()

        for user in users:
            dataset = random.sample(datasets, k=1)[0]
            problems = random.sample(dataset.problems, k=3)
            for problem in problems:
                annotation = Annotation(
                    step_labels=json.dumps(
                        [
                            random.choice(
                                ["Good", "Bad", "Neutral", "Error Realization"]
                            )
                            for _ in range(problem.num_steps)
                        ]
                    ),
                )
                problem.annotations.append(annotation)
                user.annotations.append(annotation)

        engine = create_engine("sqlite:///test_database.db")
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            for dataset in datasets:
                session.add(dataset)
            session.commit()
    else:
        engine = create_engine("sqlite:///test_database.db")
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            problems = session.exec(
                select(Problem).where(
                    Problem.solve_ratio is not None and Problem.solve_ratio < 0.2
                )
            )
            for problem in problems:
                for annotation in problem.annotations:
                    print(annotation.user.name)
