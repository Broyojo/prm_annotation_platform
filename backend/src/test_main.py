import json

import pytest
from database import get_session
from fastapi.testclient import TestClient
from main import app
from models import DatasetCreate
from sqlmodel import Session, SQLModel, StaticPool, create_engine


def pprint_json(j: dict):
    print(json.dumps(j, indent=4))


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


def test_create_dataset(client: TestClient):
    client = TestClient(app)
    response = client.post(
        "/api/datasets",
        json=DatasetCreate(
            name="Test Dataset",
            description="This is a test dataset",
            domain="Testing",
            extra_metadata={"Batch": 1},
        ).model_dump(),
    )

    pprint_json(response.json())

    assert False
