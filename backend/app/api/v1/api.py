from app.api.v1.endpoints import annotations, datasets, issues, problems, users
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(issues.router, prefix="/issues", tags=["Issues"])
api_router.include_router(problems.router, prefix="/problems", tags=["Problems"])
api_router.include_router(
    annotations.router, prefix="/annotations", tags=["Annotations"]
)
