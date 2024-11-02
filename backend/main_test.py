from typing import Callable, Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.api.dependencies import get_session
from app.main import app
from app.models.user import User


@pytest.fixture(scope="module")
def faker():
    return Faker()


@pytest.fixture(scope="function")
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(session: Session, faker: Faker) -> User:
    user = User(
        name=faker.name(),
        api_key=str(faker.uuid4()),
        permissions="admin",
        creator_id=-1,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def standard_user(session: Session, faker: Faker) -> User:
    user = User(
        name=faker.name(),
        api_key=str(faker.uuid4()),
        permissions="standard",
        creator_id=-1,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def dataset_factory(faker: Faker) -> Callable[..., Dict]:
    def create_dataset(**kwargs) -> Dict:
        return {
            "name": kwargs.get("name", faker.catch_phrase()),
            "description": kwargs.get("description", faker.text()),
            "domain": kwargs.get("domain", faker.word()),
            "extra_metadata": kwargs.get(
                "extra_metadata",
                {
                    "source": faker.company(),
                    "version": faker.random_int(min=1, max=10),
                    "tags": faker.words(3),
                },
            ),
            "problems": kwargs.get("problems", []),
        }

    return create_dataset


@pytest.fixture
def problem_factory(faker: Faker) -> Callable[..., Dict]:
    def create_problem(**kwargs) -> Dict:
        steps = faker.sentences(nb=5)
        return {
            "question": kwargs.get("question", faker.paragraph()),
            "answer": kwargs.get("answer", faker.paragraph()),
            "llm_answer": kwargs.get("llm_answer", " ".join(steps)),
            "steps": kwargs.get("steps", steps),
            "num_steps": kwargs.get("num_steps", len(steps)),
            "is_correct": kwargs.get("is_correct", faker.boolean()),
            "solve_ratio": kwargs.get(
                "solve_ratio", round(faker.random.uniform(0, 1), 2)
            ),
            "llm_name": kwargs.get("llm_name", faker.company()),
            "prompt_format": kwargs.get("prompt_format", faker.word()),
            "final_answer": kwargs.get("final_answer", {"result": faker.word()}),
            "extra_metadata": kwargs.get("extra_metadata", {"tags": faker.words()}),
            "dataset_id": kwargs.get("dataset_id", None),
        }

    return create_problem


class TestUserEndpoints:
    """Test suite for user-related endpoints"""

    def test_create_user_validation(self, client: TestClient, admin_user: User):
        """Test user creation with invalid data"""
        # Test missing required fields
        response = client.post(
            "/api/v1/users/", headers={"x-key": admin_user.api_key}, json={}
        )
        assert response.status_code == 422

        # Test invalid permissions
        response = client.post(
            "/api/v1/users/",
            headers={"x-key": admin_user.api_key},
            json={"name": "Test User", "permissions": "invalid"},
        )
        assert response.status_code == 422

    def test_user_crud_operations(
        self, client: TestClient, admin_user: User, faker: Faker
    ):
        """Test complete CRUD cycle for users"""
        # Create
        user_data = {"name": faker.name(), "permissions": "standard"}
        response = client.post(
            "/api/v1/users/", headers={"x-key": admin_user.api_key}, json=user_data
        )
        assert response.status_code == 200
        user_id = response.json()["id"]

        # Read
        response = client.get(
            f"/api/v1/users/{user_id}", headers={"x-key": admin_user.api_key}
        )
        assert response.status_code == 200
        assert response.json()["name"] == user_data["name"]

        # Update
        update_data = {"name": faker.name()}
        response = client.patch(
            f"/api/v1/users/{user_id}",
            headers={"x-key": admin_user.api_key},
            json=update_data,
        )
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]

        # Delete
        response = client.delete(
            f"/api/v1/users/{user_id}", headers={"x-key": admin_user.api_key}
        )
        assert response.status_code == 200

        # Verify deletion
        response = client.get(
            f"/api/v1/users/{user_id}", headers={"x-key": admin_user.api_key}
        )
        assert response.status_code == 404

    def test_user_permissions(self, client: TestClient, standard_user: User):
        """Test permission restrictions"""
        # Standard user shouldn't be able to create new users
        response = client.post(
            "/api/v1/users/",
            headers={"x-key": standard_user.api_key},
            json={"name": "New User"},
        )
        assert response.status_code == 403


class TestDatasetEndpoints:
    """Test suite for dataset-related endpoints"""

    def test_dataset_creation_with_problems(
        self,
        client: TestClient,
        admin_user: User,
        dataset_factory: Callable,
        problem_factory: Callable,
    ):
        """Test creating a dataset with associated problems"""
        # Create problems first
        problems_data = [problem_factory() for _ in range(3)]

        # Create dataset with problems
        dataset_data = dataset_factory()
        dataset_data["problems"] = problems_data

        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": admin_user.api_key},
            json=dataset_data,
        )
        assert response.status_code == 200
        dataset_id = response.json()["id"]

        # Verify problems were created
        response = client.get(
            f"/api/v1/datasets/{dataset_id}/problems",
            headers={"x-key": admin_user.api_key},
        )
        assert response.status_code == 200
        assert len(response.json()) == len(problems_data)


class TestProblemEndpoints:
    """Test suite for problem-related endpoints"""

    async def test_problem_steps_validation(
        self, client: TestClient, admin_user: User, problem_factory: Callable
    ):
        """Test validation of problem steps"""
        problem = problem_factory()
        problem["steps"] = []  # Empty steps list
        problem["num_steps"] = 5  # Mismatch with actual steps

        response = client.post(
            "/api/v1/problems/", headers={"x-key": admin_user.api_key}, json=problem
        )
        assert response.status_code == 422

    async def test_problem_relationships(
        self, client: TestClient, admin_user: User, problem_factory: Callable
    ):
        """Test problem relationships with annotations and issues"""
        # Create a problem
        problem = problem_factory()
        response = client.post(
            "/api/v1/problems/", headers={"x-key": admin_user.api_key}, json=problem
        )
        problem_id = response.json()["id"]

        # Create annotation
        annotation = {
            "step_labels": {"1": "first step"},
            "complete": True,
            "problem_id": problem_id,
        }
        response = client.post(
            "/api/v1/annotations/",
            headers={"x-key": admin_user.api_key},
            json=annotation,
        )
        assert response.status_code == 200

        # Create issue
        issue = {"text": "Test issue", "resolved": False, "problem_id": problem_id}
        response = client.post(
            "/api/v1/issues/", headers={"x-key": admin_user.api_key}, json=issue
        )
        assert response.status_code == 200

        # Verify relationships
        response = client.get(
            f"/api/v1/problems/{problem_id}/annotations",
            headers={"x-key": admin_user.api_key},
        )
        assert len(response.json()) == 1

        response = client.get(
            f"/api/v1/problems/{problem_id}/issues",
            headers={"x-key": admin_user.api_key},
        )
        assert len(response.json()) == 1


class TestAnnotationEndpoints:
    """Test suite for annotation-related endpoints"""

    def test_annotation_lifecycle(
        self,
        client: TestClient,
        admin_user: User,
        problem_factory: Callable,
        dataset_factory: Callable,
    ):
        """Test complete annotation lifecycle"""
        # create dataset first
        dataset = dataset_factory()
        response = client.post(
            "/api/v1/datasets/", headers={"x-key": admin_user.api_key}, json=dataset
        )
        assert response.status_code == 200
        dataset_id = response.json()["id"]

        # Create problem
        problem = problem_factory()
        problem["dataset_id"] = dataset_id
        response = client.post(
            "/api/v1/problems/", headers={"x-key": admin_user.api_key}, json=problem
        )
        problem_id = response.json()["id"]

        # Create annotation
        annotation_data = {
            "step_labels": {"1": "step one", "2": "step two"},
            "complete": False,
            "problem_id": problem_id,
        }
        response = client.post(
            "/api/v1/annotations/",
            headers={"x-key": admin_user.api_key},
            json=annotation_data,
        )
        assert response.status_code == 200
        annotation_id = response.json()["id"]

        # Update annotation
        update_data = {"step_labels": {"1": "updated step one"}, "complete": True}
        response = client.patch(
            f"/api/v1/annotations/{annotation_id}",
            headers={"x-key": admin_user.api_key},
            json=update_data,
        )
        assert response.status_code == 200
        assert response.json()["complete"] == True

        # Verify step labels were updated
        response = client.get(
            f"/api/v1/annotations/{annotation_id}",
            headers={"x-key": admin_user.api_key},
        )
        assert response.json()["step_labels"]["1"] == "updated step one"


class TestIssueEndpoints:
    """Test suite for issue-related endpoints"""

    def test_issue_resolution_workflow(
        self,
        client: TestClient,
        admin_user: User,
        problem_factory: Callable,
        dataset_factory: Callable,
    ):
        """Test issue creation and resolution workflow"""
        dataset = dataset_factory()
        response = client.post(
            "/api/v1/datasets/", headers={"x-key": admin_user.api_key}, json=dataset
        )
        assert response.status_code == 200
        dataset_id = response.json()["id"]

        # Create problem first
        problem = problem_factory()
        problem["dataset_id"] = dataset_id
        response = client.post(
            "/api/v1/problems/", headers={"x-key": admin_user.api_key}, json=problem
        )
        problem_id = response.json()["id"]

        # Create issue
        issue_data = {"text": "Test issue", "resolved": False, "problem_id": problem_id}
        response = client.post(
            "/api/v1/issues/", headers={"x-key": admin_user.api_key}, json=issue_data
        )
        assert response.status_code == 200
        issue_id = response.json()["id"]

        # Mark as resolved
        update_data = {"resolved": True}
        response = client.patch(
            f"/api/v1/issues/{issue_id}",
            headers={"x-key": admin_user.api_key},
            json=update_data,
        )
        assert response.status_code == 200
        assert response.json()["resolved"] == True


class TestSecurityFeatures:
    """Test suite for security-related features"""

    def test_api_key_validation(self, client: TestClient, admin_user: User):
        """Test API key validation"""
        # Missing API key
        response = client.get("/api/v1/users/")
        assert response.status_code == 403

        # Invalid API key
        response = client.get("/api/v1/users/", headers={"x-key": "invalid_key"})
        assert response.status_code == 401

        # Malformed API key
        response = client.get("/api/v1/users/", headers={"x-key": ""})
        assert response.status_code == 403

    def test_permission_levels(
        self, client: TestClient, admin_user: User, standard_user: User
    ):
        """Test different permission levels"""
        # Admin can create users
        response = client.post(
            "/api/v1/users/",
            headers={"x-key": admin_user.api_key},
            json={"name": "Test User"},
        )
        assert response.status_code == 200

        # Standard user cannot create users
        response = client.post(
            "/api/v1/users/",
            headers={"x-key": standard_user.api_key},
            json={"name": "Test User"},
        )
        assert response.status_code == 403


class TestDataValidation:
    """Test suite for data validation"""

    @pytest.mark.parametrize(
        "invalid_data",
        [
            # {"name": ""},  # Empty name
            # {"name": " "},  # Just whitespace
            # {"name": "a" * 256},  # Name too long
            {"permissions": "super_admin"},  # Invalid permission
        ],
    )
    def test_user_input_validation(
        self, client: TestClient, admin_user: User, invalid_data: Dict
    ):
        """Test validation of user input data"""
        response = client.post(
            "/api/v1/users/", headers={"x-key": admin_user.api_key}, json=invalid_data
        )
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"name": "", "description": "Test", "domain": "test"},  # Empty name
            {"name": "Test", "description": "", "domain": "test"},  # Empty description
            {"name": "Test", "description": "Test", "domain": ""},  # Empty domain
            {
                "name": "Test",
                "description": "Test",
                "domain": "test",
                "extra_metadata": "invalid",
            },  # Invalid metadata type
            {
                "name": "Test",
                "description": "Test",
                "domain": "test",
                "problems": "invalid",
            },  # Invalid problems type
        ],
    )
    def test_dataset_input_validation(
        self, client: TestClient, admin_user: User, invalid_data: Dict
    ):
        """Test validation of dataset input data"""
        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": admin_user.api_key},
            json=invalid_data,
        )
        assert response.status_code == 422


class TestRelationshipConstraints:
    """Test suite for relationship constraints and cascading effects"""

    def test_cascade_delete_dataset(
        self,
        client: TestClient,
        admin_user: User,
        dataset_factory: Callable,
        problem_factory: Callable,
    ):
        """Test cascading deletes when a dataset is removed"""
        # Create dataset with problems
        problems_data = [problem_factory() for _ in range(3)]
        dataset_data = dataset_factory()
        dataset_data["problems"] = problems_data

        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": admin_user.api_key},
            json=dataset_data,
        )
        assert response.status_code == 200
        dataset_id = response.json()["id"]

        # Get created problems
        response = client.get(
            f"/api/v1/datasets/{dataset_id}/problems",
            headers={"x-key": admin_user.api_key},
        )
        problem_ids = [p["id"] for p in response.json()]

        # Delete dataset
        response = client.delete(
            f"/api/v1/datasets/{dataset_id}", headers={"x-key": admin_user.api_key}
        )
        assert response.status_code == 200

        # Verify problems are also deleted
        for problem_id in problem_ids:
            response = client.get(
                f"/api/v1/problems/{problem_id}", headers={"x-key": admin_user.api_key}
            )
            assert response.status_code == 404


class TestBulkOperations:
    """Test suite for handling multiple items"""

    def test_batch_problem_creation(
        self,
        client: TestClient,
        admin_user: User,
        dataset_factory: Callable,
        problem_factory: Callable,
    ):
        """Test creating multiple problems in a dataset"""
        # Create dataset with multiple problems
        num_problems = 10
        problems_data = [problem_factory() for _ in range(num_problems)]
        dataset_data = dataset_factory()
        dataset_data["problems"] = problems_data

        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": admin_user.api_key},
            json=dataset_data,
        )
        assert response.status_code == 200
        dataset_id = response.json()["id"]

        # Verify all problems were created
        response = client.get(
            f"/api/v1/datasets/{dataset_id}/problems",
            headers={"x-key": admin_user.api_key},
        )
        assert len(response.json()) == num_problems


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    @pytest.mark.parametrize("payload_size", [1, 100, 1000])
    def test_large_payload_handling(
        self,
        client: TestClient,
        admin_user: User,
        faker: Faker,
        payload_size: int,
        dataset_factory: Callable,
    ):
        dataset = dataset_factory()
        response = client.post(
            "/api/v1/datasets/", headers={"x-key": admin_user.api_key}, json=dataset
        )
        assert response.status_code == 200
        dataset_id = response.json()["id"]

        """Test handling of large payloads"""
        # Create large text content
        large_text = faker.text() * payload_size

        # Try to create problem with large content
        problem = {
            "question": large_text,
            "answer": large_text,
            "llm_answer": large_text,
            "steps": [large_text],
            "num_steps": 1,
            "dataset_id": dataset_id,
        }

        response = client.post(
            "/api/v1/problems/", headers={"x-key": admin_user.api_key}, json=problem
        )
        assert response.status_code in [200, 413]  # Either success or payload too large

    def test_unicode_handling(self, client: TestClient, admin_user: User):
        """Test handling of Unicode characters"""
        unicode_data = {
            "name": "测试数据集",
            "description": "このデータセット",
            "domain": "테스트",
            "problems": [],
        }

        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": admin_user.api_key},
            json=unicode_data,
        )
        assert response.status_code == 200

        # Verify data was stored correctly
        dataset_id = response.json()["id"]
        response = client.get(
            f"/api/v1/datasets/{dataset_id}", headers={"x-key": admin_user.api_key}
        )
        assert response.json()["name"] == unicode_data["name"]
        assert response.json()["description"] == unicode_data["description"]

    def test_empty_collections(self, client: TestClient, admin_user: User):
        """Test handling of empty collections and null values"""
        # Create dataset with empty problems list
        response = client.post(
            "/api/v1/datasets/",
            headers={"x-key": admin_user.api_key},
            json={
                "name": "Test Dataset",
                "description": "Test Description",
                "domain": "test",
                "problems": [],
            },
        )
        assert response.status_code == 200

        # Create problem with minimal required fields
        response = client.post(
            "/api/v1/problems/",
            headers={"x-key": admin_user.api_key},
            json={
                "question": "Test?",
                "answer": "Test.",
                "llm_answer": "Test.",
                "steps": ["Step 1"],
                "num_steps": 1,
                "dataset_id": 1,
            },
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main(["-v"])
