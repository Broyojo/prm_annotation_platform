import json
import secrets

from models import *
from sqlmodel import Session, SQLModel, create_engine, insert, select

URL = "sqlite:///test_database.db"
engine = create_engine(URL, echo=True)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# class Database:
#     def __init__(self, url: str):
#         self.url = url

#         self.engine = create_engine(self.url, echo=True)
#         SQLModel.metadata.create_all(self.engine)

#         self.init_db_users()

#     def init_db_users(self):
#         with open("config.json", "r") as f:
#             config = json.load(f)

#         with Session(self.engine) as session:
#             existing_users = {
#                 user.name: user for user in session.exec(select(User)).all()
#             }

#             new_users = []
#             for user_config in config["users"]:
#                 if "name" not in user_config:
#                     print(f"WARNING: skipping user without name: {user_config}")
#                     continue

#                 if user_config["name"] not in existing_users:
#                     new_user = User(
#                         name=user_config["name"],
#                         permissions=user_config.get("permissions", "standard"),
#                         api_key=secrets.token_urlsafe(32),
#                     )
#                     new_users.append(new_user)
#                     session.add(new_user)

#             if new_users:
#                 session.commit()
#                 print("\nNew users added to database:")
#                 for user in new_users:
#                     print(f"- {user.name} (API key: {user.api_key})")

#             print("\nAll users in database:")
#             all_users = session.exec(select(User)).all()
#             for user in all_users:
#                 print(f"- {user.name} (API key: {user.api_key})")

#     def create_dataset(self, dataset: Dataset):
#         with Session(self.engine) as session:
#             session.add(dataset)
#         session.commit()

#     def read_dataset(self, dataset_id: int) -> Dataset:
#         with Session(self.engine) as session:
#             dataset = session.get(Dataset, dataset_id)
#             if not dataset:
#                 raise ValueError(f"Dataset with id {dataset_id} not found")
#             return dataset

#     def update_dataset(self, dataset_id: int, dataset: Dataset):
#         with Session(self.engine) as session:
#             existing_dataset = session.get(Dataset, dataset_id)
#             if not existing_dataset:
#                 raise ValueError(f"Dataset with id {dataset_id} not found")
#             for field, value in dataset.__dict__.items():
#                 if field != "id" and not field.startswith("_"):
#                     setattr(existing_dataset, field, value)
#             session.commit()

#     def delete_dataset(self, dataset_id: int):
#         with Session(self.engine) as session:
#             dataset = session.get(Dataset, dataset_id)
#             if not dataset:
#                 raise ValueError(f"Dataset {dataset_id} not found")
#             session.delete(dataset)
#             session.commit()


# if __name__ == "__main__":
#     db = Database(url="sqlite:///test_database.db")
