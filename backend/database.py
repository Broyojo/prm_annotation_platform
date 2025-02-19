import json
import os
import secrets
from typing import Optional

import nltk
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
from sqlalchemy import text
from utils import report_timestamp
from config import database_file

import pdb


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(unique=True, index=True)
    # admin/dev/annotation/review
    access: str
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
    model_config = {"protected_namespaces": ()}  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    category: str # demonstration/screening/annotation
    question: str
    answer: str
    model_answer: str = Field(unique=True)
    model_answer_steps: str  # json list of steps
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    model_name: Optional[str] = None
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
    engine = create_engine(database_file)
    SQLModel.metadata.create_all(engine)

    # Update users
    with open("users.json", "r") as f:
        users = json.load(f)

    with Session(engine) as session:
        try:
            for user_data in users:
                # Check if user exists
                user_search_command = text("SELECT user.id, user.name, user.api_key, user.access FROM user where user.name='{}'".format(user_data["name"]))
                existing_user = session.exec(
                    select(User).where(User.name == user_data["name"])
                ).first()

                if existing_user is None:
                    new_user = User(
                        name=user_data["name"], api_key=secrets.token_urlsafe(32)
                    )
                    session.add(new_user)
                    print(f"Added new user: {user_data['name']} api_key: {new_user.api_key}")

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
                    # Check if problem exists (using model_answer as unique identifier)
                    existing_problem = session.exec(
                        select(Problem).where(
                            Problem.model_answer == problem_data["model_answer"]
                        )
                    ).first()

                    if existing_problem is None:
                        new_problem = Problem(
                            question=problem_data["question"],
                            answer=problem_data["answer"],
                            model_answer=problem_data["model_answer"],
                            model_answer_steps=(
                                json.dumps(
                                    problem_data["model_answer_steps"]
                                    if "model_answer_steps" in problem_data
                                    else nltk.sent_tokenize(problem_data["model_answer"]
                                    )
                                )
                            ),
                            is_correct=problem_data.get("is_correct"),
                            solve_ratio=problem_data.get("solve_ratio"),
                            model_name=problem_data.get("model_name"),
                            prompt_format=problem_data.get("prompt_format"),
                            final_answer=json.dumps(problem_data.get("final_answer")),
                            time_added=json.dumps(report_timestamp()),
                            dataset=existing_dataset,
                        )
                        session.add(new_problem)
                        print(f"Added new problem to dataset {dataset_name}")

                session.commit()

            except Exception as e:
                session.rollback()
                print(f"Error processing dataset {dataset_name}: {e}")
                raise e


def download_database(engine=None):
    """Downloads the entire database into a structured JSON file.
    Format:
    {
        "datasets": [
            {
                "name": "Dataset Name",
                "domain": "STEM",
                "problems": [
                    {
                        "question": "...",
                        "answer": "...",
                        "model_answer": "...",
                        "model_answer_steps": [...],
                        "is_correct": true/false,
                        "solve_ratio": 0.8,
                        "model_answer": "...",
                        "prompt_format": "...",
                        "final_answer": "...",
                        "annotations": [
                            {
                                "user": "username",
                                "step_labels": {...},
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    if engine is None:
        engine = create_engine(database_file)

    with Session(engine) as session:
        # Get all datasets
        datasets_query = select(Dataset)
        datasets = session.exec(datasets_query).all()

        output = {"datasets": []}

        for dataset in datasets:
            dataset_dict = {
                "name": dataset.name,
                "domain": dataset.domain,
                "problems": [],
            }

            # Get all problems for this dataset
            problems_query = select(Problem).where(Problem.dataset_id == dataset.id)
            problems = session.exec(problems_query).all()

            for problem in problems:
                problem_dict = {
                    "question": problem.question,
                    "answer": problem.answer,
                    "model_answer": problem.model_answer,
                    "model_answer_steps": json.loads(problem.model_answer_steps),
                    "is_correct": problem.is_correct,
                    "solve_ratio": problem.solve_ratio,
                    "model_name": problem.model_name,
                    "prompt_format": problem.prompt_format,
                    "final_answer": (
                        json.loads(problem.final_answer)
                        if problem.final_answer
                        else None
                    ),
                    "annotations": [],
                }

                # Get all annotations for this problem
                annotations_query = select(Annotation).where(
                    Annotation.problem_id == problem.id
                )
                annotations = session.exec(annotations_query).all()

                for annotation in annotations:
                    # Get user name instead of ID
                    user_query = select(User).where(User.id == annotation.user_id)
                    user = session.exec(user_query).first()

                    if not user:
                        print("missing user for annotation:", annotation)
                        continue

                    annotation_dict = {
                        "user": user.name,
                        "step_labels": (
                            json.loads(annotation.step_labels)
                            if annotation.step_labels
                            else {}
                        ),
                    }
                    problem_dict["annotations"].append(annotation_dict)

                dataset_dict["problems"].append(problem_dict)

            output["datasets"].append(dataset_dict)

        return output


if __name__ == "__main__":
    update_database()
    output = download_database()
    
    # Write to file
    # output_path = "prmbench_export.json"
    # with open(output_path, "w") as f:
    #     json.dump(output, f, indent=4)

    # print(f"Database exported to {output_path}")
