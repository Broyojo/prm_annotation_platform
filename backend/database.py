from typing import Optional

import nltk
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

    WRITE = False

    if WRITE:
        from faker import Faker

        faker = Faker()

        users = []
        for _ in range(10):
            user = User(
                name=faker.name(), api_key=str(faker.uuid4()), permissions="standard"
            )
            users.append(user)

        dataset = Dataset(name="Test Dataset", domain="math")

        with open("./testing/test_data.json", "r") as f:
            data = json.load(f)

        for d in data:
            steps = nltk.sent_tokenize(d["model_answer"])
            problem = Problem(
                question=d["question"],
                answer=d["answer"],
                llm_answer=d["model_answer"],
                steps=json.dumps(steps),
                num_steps=len(steps),
                is_correct=d.get("is_correct"),
                solve_ratio=d.get("solve_ratio"),
                llm_name=d.get("model_name"),
                prompt_format=d.get("prompt_format"),
                final_answer=json.dumps(d.get("final_answer")),
            )
            dataset.problems.append(problem)

        for user in users:
            # pick random subset of problems for each to annotate with random labeling
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

        engine = create_engine("sqlite:///database.db")
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            session.add(dataset)
            session.commit()
    else:
        engine = create_engine("sqlite:///database.db")
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
