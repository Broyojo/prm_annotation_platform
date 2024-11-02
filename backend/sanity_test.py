import json
import random
from typing import Callable

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.api.dependencies import get_session
from app.main import app

# Import your models and app here
from app.models.user import User
from app.schemas.annotation import AnnotationCreate
from app.schemas.dataset import DatasetCreate
from app.schemas.issue import IssueCreate
from app.schemas.problem import ProblemCreate
from app.schemas.user import UserCreate


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
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
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
    def _create_user(**kwargs) -> UserCreate:
        return UserCreate(
            name=kwargs.get("name", faker.name()),
            api_key=kwargs.get("api_key", str(faker.uuid4())),
            permissions=kwargs.get("permissions", random.choice(["standard", "admin"])),
        )

    return _create_user


@pytest.fixture
def fake_admin_user(session: Session, fake_user) -> User:
    """
    Create a fake admin user with randomized data and API key
    """
    user = User(**fake_user(permissions="admin").model_dump(), creator_id=-1)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def fake_dataset(faker) -> Callable[..., DatasetCreate]:
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
    def _create_problem(**kwargs) -> ProblemCreate:
        steps = faker.sentences(nb=10)
        return ProblemCreate(
            question=kwargs.get("question", faker.paragraph()),
            answer=kwargs.get("answer", faker.paragraph()),
            llm_answer=" ".join(steps),
            steps=steps,
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
                {
                    "source": faker.company(),
                    "version": faker.random_int(min=1, max=10),
                    "tags": faker.words(3),
                },
            ),
            dataset_id=kwargs.get("dataset_id", None),
        )

    return _create_problem


@pytest.fixture
def fake_annotation(faker) -> Callable[..., AnnotationCreate]:
    def _create_annotation(**kwargs) -> AnnotationCreate:
        return AnnotationCreate(
            step_labels=kwargs.get(
                "step_labels", {str(i): faker.word() for i in range(5)}
            ),
            complete=kwargs.get("complete", faker.boolean()),
            problem_id=kwargs.get("problem_id", 1),
        )

    return _create_annotation


@pytest.fixture
def fake_issue(faker) -> Callable[..., IssueCreate]:
    def _create_issue(**kwargs) -> IssueCreate:
        return IssueCreate(
            text=kwargs.get("text", faker.text()),
            resolved=kwargs.get("resolved", faker.boolean()),
            problem_id=kwargs.get("problem_id", 1),
        )

    return _create_issue


class TestUsers:
    def test_create_user(self, client: TestClient, fake_user, fake_admin_user):
        user = fake_user()
        response = client.post(
            "/api/v1/users/",
            headers={"x-key": fake_admin_user.api_key},
            json=user.model_dump(),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == user.name
        assert data["permissions"] == user.permissions
        return data

    def test_read_users(self, client: TestClient, fake_admin_user):
        response = client.get(
            "/api/v1/users/", headers={"x-key": fake_admin_user.api_key}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_read_user(self, client: TestClient, fake_user, fake_admin_user):
        created_user = self.test_create_user(client, fake_user, fake_admin_user)
        response = client.get(
            f"/api/v1/users/{created_user['id']}",
            headers={"x-key": fake_admin_user.api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["name"] == created_user["name"]

    def test_update_user(self, client: TestClient, fake_user, fake_admin_user):
        created_user = self.test_create_user(client, fake_user, fake_admin_user)
        update_data = {"name": "Updated Name"}
        response = client.patch(
            f"/api/v1/users/{created_user['id']}",
            headers={"x-key": fake_admin_user.api_key},
            json=update_data,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_user(self, client: TestClient, fake_user, fake_admin_user):
        created_user = self.test_create_user(client, fake_user, fake_admin_user)
        response = client.delete(
            f"/api/v1/users/{created_user['id']}",
            headers={"x-key": fake_admin_user.api_key},
        )
        assert response.status_code == 200


class TestDatasets:
    def test_create_dataset(self, client: TestClient, fake_dataset, fake_admin_user):
        dataset = fake_dataset()
        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": fake_admin_user.api_key},
            json=dataset.model_dump(),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == dataset.name
        assert data["description"] == dataset.description
        return data

    def test_read_datasets(self, client: TestClient, fake_admin_user):
        response = client.get(
            "/api/v1/datasets/", headers={"x-key": fake_admin_user.api_key}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_read_dataset(self, client: TestClient, fake_dataset, fake_admin_user):
        created_dataset = self.test_create_dataset(
            client, fake_dataset, fake_admin_user
        )
        response = client.get(
            f"/api/v1/datasets/{created_dataset['id']}",
            headers={"x-key": fake_admin_user.api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_dataset["id"]
        assert data["name"] == created_dataset["name"]


class TestProblems:
    def test_create_problem(
        self, client: TestClient, fake_problem, fake_dataset, fake_admin_user
    ):
        # First create a dataset to associate with the problem
        dataset_response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": fake_admin_user.api_key},
            json=fake_dataset().model_dump(),
        )
        dataset_id = dataset_response.json()["id"]

        problem = fake_problem(dataset_id=dataset_id)
        response = client.post(
            "/api/v1/problems/",
            headers={"x-key": fake_admin_user.api_key},
            json=problem.model_dump(),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == problem.question
        assert data["answer"] == problem.answer
        return data

    def test_read_problems(self, client: TestClient, fake_admin_user):
        response = client.get(
            "/api/v1/problems/", headers={"x-key": fake_admin_user.api_key}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_read_problem(
        self, client: TestClient, fake_problem, fake_dataset, fake_admin_user
    ):
        created_problem = self.test_create_problem(
            client, fake_problem, fake_dataset, fake_admin_user
        )
        response = client.get(
            f"/api/v1/problems/{created_problem['id']}",
            headers={"x-key": fake_admin_user.api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_problem["id"]
        assert data["question"] == created_problem["question"]


class TestAnnotations:
    def test_create_annotation(
        self,
        client: TestClient,
        fake_annotation,
        fake_problem,
        fake_dataset,
        fake_admin_user,
    ):
        problem = TestProblems.test_create_problem(
            TestProblems(), client, fake_problem, fake_dataset, fake_admin_user
        )

        annotation = fake_annotation(problem_id=problem["id"])
        response = client.post(
            "/api/v1/annotations/",
            headers={"x-key": fake_admin_user.api_key},
            json=annotation.model_dump(),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["problem_id"] == annotation.problem_id
        return data

    def test_read_annotations(self, client: TestClient, fake_admin_user):
        response = client.get(
            "/api/v1/annotations/", headers={"x-key": fake_admin_user.api_key}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_read_annotation(
        self,
        client: TestClient,
        fake_annotation,
        fake_problem,
        fake_dataset,
        fake_admin_user,
    ):
        created_annotation = self.test_create_annotation(
            client, fake_annotation, fake_problem, fake_dataset, fake_admin_user
        )
        response = client.get(
            f"/api/v1/annotations/{created_annotation['id']}",
            headers={"x-key": fake_admin_user.api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_annotation["id"]


class TestIssues:
    def test_create_issue(
        self,
        client: TestClient,
        fake_issue,
        fake_problem,
        fake_dataset,
        fake_admin_user,
    ):
        problem = TestProblems.test_create_problem(
            TestProblems(), client, fake_problem, fake_dataset, fake_admin_user
        )

        issue = fake_issue(problem_id=problem["id"])
        response = client.post(
            "/api/v1/issues/",
            headers={"x-key": fake_admin_user.api_key},
            json=issue.model_dump(),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["problem_id"] == issue.problem_id
        return data

    def test_read_issues(self, client: TestClient, fake_admin_user):
        response = client.get(
            "/api/v1/issues/", headers={"x-key": fake_admin_user.api_key}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_read_issue(
        self,
        client: TestClient,
        fake_issue,
        fake_problem,
        fake_dataset,
        fake_admin_user,
    ):
        created_issue = self.test_create_issue(
            client, fake_issue, fake_problem, fake_dataset, fake_admin_user
        )
        response = client.get(
            f"/api/v1/issues/{created_issue['id']}",
            headers={"x-key": fake_admin_user.api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_issue["id"]


# Test relationships
def test_user_problems(client: TestClient, fake_user, fake_admin_user):
    user = TestUsers.test_create_user(TestUsers(), client, fake_user, fake_admin_user)
    response = client.get(
        f"/api/v1/users/{user['id']}/problems",
        headers={"x-key": fake_admin_user.api_key},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_user_annotations(client: TestClient, fake_user, fake_admin_user):
    user = TestUsers.test_create_user(TestUsers(), client, fake_user, fake_admin_user)
    response = client.get(
        f"/api/v1/users/{user['id']}/annotations",
        headers={"x-key": fake_admin_user.api_key},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dataset_problems(client: TestClient, fake_dataset, fake_admin_user):
    dataset = TestDatasets.test_create_dataset(
        TestDatasets(), client, fake_dataset, fake_admin_user
    )
    response = client.get(
        f"/api/v1/datasets/{dataset['id']}/problems",
        headers={"x-key": fake_admin_user.api_key},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_problem_annotations(
    client: TestClient, fake_problem, fake_dataset, fake_admin_user
):
    problem = TestProblems.test_create_problem(
        TestProblems(), client, fake_problem, fake_dataset, fake_admin_user
    )
    response = client.get(
        f"/api/v1/problems/{problem['id']}/annotations",
        headers={"x-key": fake_admin_user.api_key},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dataset_issues(client: TestClient, fake_dataset, fake_admin_user):
    dataset = TestDatasets.test_create_dataset(
        TestDatasets(), client, fake_dataset, fake_admin_user
    )
    response = client.get(
        f"/api/v1/datasets/{dataset['id']}/issues",
        headers={"x-key": fake_admin_user.api_key},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_problem_issues(
    client: TestClient, fake_problem, fake_dataset, fake_admin_user
):
    problem = TestProblems.test_create_problem(
        TestProblems(), client, fake_problem, fake_dataset, fake_admin_user
    )
    response = client.get(
        f"/api/v1/problems/{problem['id']}/issues",
        headers={"x-key": fake_admin_user.api_key},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Error case tests
def test_invalid_user_id(client: TestClient, fake_admin_user):
    response = client.get(
        "/api/v1/users/999999", headers={"x-key": fake_admin_user.api_key}
    )
    assert response.status_code == 404


def test_invalid_dataset_id(client: TestClient, fake_admin_user):
    response = client.get(
        "/api/v1/datasets/999999", headers={"x-key": fake_admin_user.api_key}
    )
    assert response.status_code == 404


def test_invalid_problem_id(client: TestClient, fake_admin_user):
    response = client.get(
        "/api/v1/problems/999999", headers={"x-key": fake_admin_user.api_key}
    )
    assert response.status_code == 404


def test_invalid_annotation_id(client: TestClient, fake_admin_user):
    response = client.get(
        "/api/v1/annotations/999999", headers={"x-key": fake_admin_user.api_key}
    )
    assert response.status_code == 404


def test_invalid_issue_id(client: TestClient, fake_admin_user):
    response = client.get(
        "/api/v1/issues/999999", headers={"x-key": fake_admin_user.api_key}
    )
    assert response.status_code == 404


def test_unauthorized_access(client: TestClient):
    # Try to access without API key
    response = client.get("/api/v1/users/")
    assert response.status_code == 403

    # Try to access with invalid API key
    response = client.get("/api/v1/users/", headers={"x-key": "invalid_key"})
    assert response.status_code == 401


def test_invalid_problem_creation(client: TestClient, fake_problem, fake_admin_user):
    # Try to create problem without dataset_id
    problem = fake_problem(dataset_id=None)
    try:
        response = client.post(
            "/api/v1/problems/",
            headers={"x-key": fake_admin_user.api_key},
            json=problem.model_dump(),
        )
        assert False
    except:
        pass


def test_invalid_annotation_creation(
    client: TestClient, fake_annotation, fake_admin_user
):
    # Try to create annotation without problem_id
    try:
        annotation = fake_annotation(problem_id=None)
        response = client.post(
            "/api/v1/annotations/",
            headers={"x-key": fake_admin_user.api_key},
            json=annotation.model_dump(),
        )
        assert False
    except:
        pass


def test_invalid_issue_creation(client: TestClient, fake_issue, fake_admin_user):
    # Try to create issue without problem_id
    try:
        issue = fake_issue(problem_id=None)
        response = client.post(
            "/api/v1/issues/",
            headers={"x-key": fake_admin_user.api_key},
            json=issue.model_dump(),
        )
        print(response)
        assert False
    except:
        pass
