import json
import secrets

from models import User
from sqlmodel import Session, SQLModel, create_engine, select


def init_db():
    with open("config.json", "r") as f:
        config = json.load(f)

    engine = create_engine("sqlite:///test_database.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_users = {user.name: user for user in session.exec(select(User)).all()}

        new_users = []
        for user_config in config["users"]:
            if "name" not in user_config:
                print(f"WARNING: skipping user without name: {user_config}")
                continue

            if user_config["name"] not in existing_users:
                new_user = User(
                    name=user_config["name"],
                    permissions=user_config.get("permissions", "standard"),
                    api_key=secrets.token_urlsafe(32),
                )
                new_users.append(new_user)
                session.add(new_user)

        if new_users:
            session.commit()
            print("\nNew users added to database:")
            for user in new_users:
                print(f"- {user.name} (API key: {user.api_key})")

        print("\nAll users in database:")
        all_users = session.exec(select(User)).all()
        for user in all_users:
            print(f"- {user.name} (API key: {user.api_key})")


if __name__ == "__main__":
    init_db()
