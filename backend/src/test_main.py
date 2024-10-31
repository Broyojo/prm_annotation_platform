import json
import random
from datetime import datetime
from typing import Callable

import pytest
from database import get_session
from faker import Faker
from fastapi.testclient import TestClient
from main import app
from models import DatasetCreate, ProblemCreate, User, UserCreate
from sqlmodel import Session, SQLModel, StaticPool, create_engine


def pprint_json(*values: object, **kwargs):
    print(
        *[json.dumps(value, indent=4) for value in values],
        **kwargs,
    )


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        url="sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def fake_user(faker: Faker) -> Callable[..., UserCreate]:
    """
    Generate fake user
    """

    def _create_user(**kwargs) -> UserCreate:
        return UserCreate(
            name=kwargs.get("name", faker.name()),
            api_key=kwargs.get("api_key", str(faker.uuid4())),
            permissions=kwargs.get("permissions", random.choice(["standard", "admin"])),
        )

    return _create_user


@pytest.fixture
def fake_admin_user(session: Session, fake_user):
    """
    Create a fake admin user with randomized data
    """
    user = fake_user(permissions="admin").to_db_model()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def fake_dataset(faker) -> Callable[..., DatasetCreate]:
    """
    Generate fake dataset metadata
    """

    def _create_dataset(**kwargs) -> DatasetCreate:
        return DatasetCreate(
            name=kwargs.get("name", faker.catch_phrase()),
            description=kwargs.get("description", faker.text()),
            domain=kwargs.get("domain", faker.word()),
            extra_metadata=kwargs.get(
                "extra_metadata",
                {
                    "source": faker.company(),
                    "version": faker.random_int(min=1, max=10),
                    "tags": faker.words(3),
                },
            ),
            problems=kwargs.get("problems", []),
        )

    return _create_dataset


@pytest.fixture
def fake_problem(faker) -> Callable[..., ProblemCreate]:
    """
    Generate fake problem metadata
    """

    def _create_problem(**kwargs) -> ProblemCreate:
        steps = faker.sentences(nb=10)
        return ProblemCreate(
            question=kwargs.get("question", faker.paragraph()),
            answer=kwargs.get("answer", faker.paragraph()),
            llm_answer=" ".join(steps),
            steps={i: step for i, step in enumerate(steps)},
            num_steps=len(steps),
            is_correct=kwargs.get("is_correct", faker.boolean()),
            solve_ratio=kwargs.get("solve_ratio", faker.pyfloat()),
            llm_name=kwargs.get("llm_name", faker.domain_name()),
            prompt_format=kwargs.get("prompt_format", faker.catch_phrase()),
            final_answer=kwargs.get(
                "final_answer", {"answers": faker.random_letters()}
            ),
            extra_metadata=kwargs.get(
                "extra_metadata",
                kwargs.get(
                    "extra_metadata",
                    {
                        "source": faker.company(),
                        "version": faker.random_int(min=1, max=10),
                        "tags": faker.words(3),
                    },
                ),
            ),
        )

    return _create_problem


# User Tests
def test_users(client: TestClient, fake_admin_user: User, fake_user):
    users = [fake_user() for _ in range(random.randint(0, 100))]

    users_public = []

    # write all users to database
    for user in users:
        response = client.post(
            "/api/users",
            headers={"x-key": fake_admin_user.api_key},
            json=user.model_dump(),
        )
        data = response.json()
        pprint_json("POST /api/users:", data)
        assert response.status_code == 200
        assert data["name"] == user.name
        assert data["permissions"] == user.permissions
        assert data["api_key"] == user.api_key

    users.append(fake_admin_user)

    # read all users
    response = client.get("/api/users", headers={"x-key": fake_admin_user.api_key})
    data = response.json()
    pprint_json("GET /api/users:", data)
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == len(users)  # include fake admin user

    users = data

    # read specific user
    for user in users:
        response = client.get(
            f"/api/users/{user["id"]}",
            headers={"x-key": user["api_key"]},
        )
        data = response.json()
        pprint_json(data)
        assert response.status_code == 200
        assert data["name"] == user["name"]
        assert data["permissions"] == user["permissions"]
        assert data["id"] == user["id"]
        assert data["created_at"] == user["created_at"]
        assert data["last_modified"] == user["last_modified"]

    # read unknown user


def test_create_user(client: TestClient, fake_admin_user: User):
    pass


# def test_create_dataset(
#     client: TestClient, test_user: User, fake_dataset, fake_problem
# ):
#     problems = [fake_problem() for _ in range(random.randint(0, 100))]

#     dataset = fake_dataset(problems=problems)

#     dataset_dict = dataset.model_dump()

#     response = client.post(
#         "/api/datasets",
#         headers={"x-key": test_user.api_key},
#         json=dataset_dict,
#     )

#     data = response.json()
#     assert response.status_code == 200
#     assert data["name"] == dataset.name
#     assert data["description"] == dataset.description
#     assert data["domain"] == dataset.domain
#     assert data["extra_metadata"] == dataset.extra_metadata
#     assert data["creator_id"] == test_user.id
