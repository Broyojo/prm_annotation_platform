import json
import secrets

from models import Annotation, Dataset, Problem, User
from sqlmodel import Session, SQLModel, create_engine, select


def init_db():
    """Initialize the database and sync users from config.json, only adding new users"""
    with open("config.json", "r") as f:
        config = json.load(f)

    engine = create_engine("sqlite:///test_database.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_users = {user.name: user for user in session.exec(select(User)).all()}

        new_users = []
        for user_config in config["users"]:
            if user_config["name"] not in existing_users:
                new_user = User(
                    name=user_config["name"],
                    permissions=user_config["permissions"],
                    api_key=secrets.token_urlsafe(32),
                )
                new_users.append(new_user)
                session.add(new_user)

        if new_users:
            session.commit()
            for user in new_users:
                print(f"- {user.name} (API key: {user.api_key})")

        print("All users in database:")
        all_users = session.exec(select(User)).all()
        for user in all_users:
            print(f"- {user.name} (API key: {user.api_key})")


if __name__ == "__main__":
    init_db()

    # quit()

    # WRITE = True

    # if WRITE:
    #     from faker import Faker

    #     faker = Faker()

    #     users: list[User] = []
    #     for _ in range(10):
    #         user = User(
    #             name=faker.name(),
    #             api_key=secrets.token_urlsafe(32),
    #             permissions="standard",
    #         )
    #         users.append(user)

    #     users.append(
    #         User(
    #             name="David Andrews",
    #             api_key=secrets.token_urlsafe(32),
    #             permissions="admin",
    #         )
    #     )

    #     print("Users:")
    #     for user in users:
    #         print(user)
    #     print()

    #     datasets = []
    #     for file in os.listdir("./test_data/normalized"):
    #         path = os.path.join("./test_data/normalized", file)
    #         dataset = Dataset(
    #             name=file.split(".")[0]
    #             .replace("_", " ")
    #             .replace("selected", "")
    #             .strip()
    #             .title(),
    #             description="a dataset",
    #             domain="math",
    #             creator=users[-1],
    #             upload_date=datetime.now(),
    #             extra_metadata=json.dumps({"batch": 1}),
    #         )

    #         with open(path, "r") as f:
    #             problems = json.load(f)

    #         for problem in problems:
    #             dataset.problems.append(
    #                 Problem(
    #                     question=problem["question"],
    #                     answer=problem["answer"],
    #                     llm_answer=problem["llm_answer"],
    #                     steps=json.dumps(problem["steps"]),
    #                     num_steps=problem["num_steps"],
    #                     is_correct=problem.get("is_correct"),
    #                     solve_ratio=problem.get("solve_ratio"),
    #                     llm_name=problem.get("llm_name"),
    #                     prompt_format=problem.get("prompt_format"),
    #                     final_answer=json.dumps(problem.get("final_answer")),
    #                     extra_metadata="",
    #                 )
    #             )

    #         datasets.append(dataset)

    #     print("Datasets:")
    #     for dataset in datasets:
    #         print(dataset)
    #         print("Num problems:", len(dataset.problems))
    #     print()

    #     for user in users:
    #         dataset = random.sample(datasets, k=1)[0]
    #         problems = random.sample(dataset.problems, k=3)
    #         for problem in problems:
    #             annotation = Annotation(
    #                 step_labels=json.dumps(
    #                     [
    #                         random.choice(
    #                             ["Good", "Bad", "Neutral", "Error Realization"]
    #                         )
    #                         for _ in range(problem.num_steps)
    #                     ]
    #                 ),
    #             )
    #             problem.annotations.append(annotation)
    #             user.annotations.append(annotation)

    #     engine = create_engine("sqlite:///test_database.db")
    #     SQLModel.metadata.create_all(engine)

    #     with Session(engine) as session:
    #         for dataset in datasets:
    #             session.add(dataset)
    #         session.commit()
    # else:
    #     engine = create_engine("sqlite:///test_database.db")
    #     SQLModel.metadata.create_all(engine)

    #     with Session(engine) as session:
    #         problems = session.exec(
    #             select(Problem).where(
    #                 Problem.solve_ratio is not None and Problem.solve_ratio < 0.2
    #             )
    #         )
    #         for problem in problems:
    #             for annotation in problem.annotations:
    #                 print(annotation.user.name)
