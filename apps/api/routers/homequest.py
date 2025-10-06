"""Routes exposing the HomeQuest retrofit planning APIs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.homequest import GoalDefinition, HomeQuestPlan, HomeQuestRequest
from ..services.homequest import planner


router = APIRouter(prefix="/homequest", tags=["HomeQuest"])


@router.get("/goals", response_model=list[GoalDefinition])
def list_goals() -> list[GoalDefinition]:
    """Return the library of supported goals so clients can build UIs."""

    return planner.list_goal_definitions()


@router.post("/plan", response_model=HomeQuestPlan)
def create_plan(request: HomeQuestRequest) -> HomeQuestPlan:
    """Run the HomeQuest planner and store the resulting retrofit roadmap."""

    return planner.create_plan(request)


@router.get("/plan/{plan_id}", response_model=HomeQuestPlan)
def get_plan(plan_id: str) -> HomeQuestPlan:
    """Retrieve a stored plan by id."""

    try:
        return planner.fetch_plan(plan_id)
    except KeyError as exc:  # pragma: no cover - FastAPI converts to 404
        raise HTTPException(status_code=404, detail=str(exc)) from exc

