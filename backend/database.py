import json
import os
import secrets
from typing import Optional

import nltk
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(unique=True, index=True)
    api_key: str = Field(unique=True, index=True)

    # a user can have many annotations
    annotations: list["Annotation"] = Relationship(back_populates="user")


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    step_labels: str  # json objects of step index => label per step

    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="annotations")

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="annotations")


class Problem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    question: str
    answer: str
    llm_answer: str = Field(unique=True)
    steps: str  # json list of steps
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


# [Previous model definitions remain the same]


def update_database():
    # Initialize database
    engine = create_engine("sqlite:///prmbench_database.db")
    SQLModel.metadata.create_all(engine)

    # Update users
    with open("users.json", "r") as f:
        users = json.load(f)

    with Session(engine) as session:
        try:
            for user_data in users:
                # Check if user exists
                existing_user = session.exec(
                    select(User).where(User.name == user_data["name"])
                ).first()

                if existing_user is None:
                    new_user = User(
                        name=user_data["name"], api_key=secrets.token_urlsafe(32)
                    )
                    session.add(new_user)
                    print(f"Added new user: {user_data['name']}")

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error updating users: {e}")
            raise e

    # Process datasets and problems
    problems_dir = "./selected_samples"

    for file in os.listdir(problems_dir):
        path = os.path.join(problems_dir, file)

        dataset_name = (
            file.split(".")[0].replace("_", " ").replace("selected", "").strip().title()
        )

        with Session(engine) as session:
            try:
                # Check if dataset exists
                existing_dataset = session.exec(
                    select(Dataset).where(Dataset.name == dataset_name)
                ).first()

                if existing_dataset is None:
                    existing_dataset = Dataset(name=dataset_name, domain="STEM")
                    session.add(existing_dataset)
                    print(f"Added new dataset: {dataset_name}")

                # Load problems from file
                with open(path, "r") as f:
                    if file.endswith(".jsonl"):
                        problems_data = [json.loads(line) for line in f.readlines()]
                    else:
                        problems_data = json.load(f)

                # Process each problem
                for problem_data in problems_data:
                    # Check if problem exists (using llm_answer as unique identifier)
                    existing_problem = session.exec(
                        select(Problem).where(
                            Problem.llm_answer == problem_data["model_answer"]
                        )
                    ).first()

                    if existing_problem is None:
                        new_problem = Problem(
                            question=problem_data["question"],
                            answer=problem_data["answer"],
                            llm_answer=problem_data["model_answer"],
                            steps=(
                                json.dumps(
                                    problem_data["model_answer_steps"]
                                    if "model_answer_steps" in problem_data
                                    else nltk.sent_tokenize(
                                        problem_data["model_answer"]
                                    )
                                )
                            ),
                            is_correct=problem_data.get("is_correct"),
                            solve_ratio=problem_data.get("solve_ratio"),
                            llm_name=problem_data.get("model_name"),
                            prompt_format=problem_data.get("prompt_format"),
                            final_answer=json.dumps(problem_data.get("final_answer")),
                            dataset=existing_dataset,
                        )
                        session.add(new_problem)
                        print(f"Added new problem to dataset {dataset_name}")

                session.commit()

            except Exception as e:
                session.rollback()
                print(f"Error processing dataset {dataset_name}: {e}")
                raise e


if __name__ == "__main__":
    update_database()
