from pathlib import Path
import sys

# Ensure the repository root is on sys.path so ``apps`` can be imported when tests
# are executed from the project root.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.schemas.homequest import (  # noqa: E402
    GoalType,
    HomeProfile,
    HomeQuestRequest,
)
from apps.api.services.homequest import HomeQuestPlanner  # noqa: E402


def sample_request() -> HomeQuestRequest:
    profile = HomeProfile(
        name="Ellerbe Residence",
        address="123 Example St",
        city="Washington",
        state="DC",
        postal_code="20001",
        occupancy_type="single_family",
        square_feet=1800,
        built_year=1985,
        bedrooms=3,
        occupants=3,
        insulation_level="average",
        hvac_type="Gas furnace",
        water_heater="Gas tank",
        average_monthly_bill=210.0,
        has_rooftop_solar=False,
    )
    return HomeQuestRequest(
        home=profile,
        goals=[GoalType.LOWER_BILLS, GoalType.DECARBONIZE],
        annual_budget=12000,
        preferred_timeline_months=18,
    )


def test_list_goal_definitions_covers_all_enum():
    planner = HomeQuestPlanner()
    goals = planner.list_goal_definitions()
    assert {item.goal for item in goals} == set(GoalType)


def test_create_plan_persists_for_fetch():
    planner = HomeQuestPlanner()
    request = sample_request()

    plan = planner.create_plan(request)

    assert plan.scorecard.target_score >= plan.scorecard.baseline_score
    assert plan.priority_actions  # at least one recommendation

    fetched = planner.fetch_plan(plan.plan_id)
    assert fetched == plan
