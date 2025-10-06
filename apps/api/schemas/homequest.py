"""Pydantic models for the HomeQuest planning feature."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, validator


class GoalType(str, Enum):
    """Enumerates the sustainability focus areas a homeowner can pick from."""

    LOWER_BILLS = "lower_bills"
    COMFORT = "comfort"
    RESILIENCE = "resilience"
    DECARBONIZE = "decarbonize"
    ELECTRIFY = "electrify"


class OccupancyType(str, Enum):
    """Basic occupancy types supported by the planner."""

    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    MIXED_USE = "mixed_use"


class InsulationLevel(str, Enum):
    """Quick way for users to describe their building envelope."""

    POOR = "poor"
    AVERAGE = "average"
    GOOD = "good"


class HomeProfile(BaseModel):
    """Describes the existing conditions for a property."""

    name: str = Field(..., description="Nickname for the property (helps with plan storage)")
    address: str = Field(..., description="Street address for context in the narrative output")
    city: str
    state: str = Field(..., min_length=2, max_length=2, description="Two letter state code")
    postal_code: str = Field(..., regex=r"^\d{5}$", description="US ZIP code")
    occupancy_type: OccupancyType = OccupancyType.SINGLE_FAMILY
    square_feet: PositiveInt
    built_year: int = Field(..., ge=1850, le=2050)
    bedrooms: Optional[int] = Field(None, ge=0)
    occupants: Optional[int] = Field(None, ge=0)
    insulation_level: InsulationLevel = InsulationLevel.AVERAGE
    hvac_type: str = Field(..., description="Primary heating and cooling system")
    water_heater: Optional[str] = None
    average_monthly_bill: PositiveFloat = Field(
        ..., description="Typical combined electric + gas monthly bill in USD"
    )
    peak_energy_use_month: Optional[str] = Field(
        None, description="Month name representing the highest utility spend"
    )
    has_rooftop_solar: bool = False
    has_ev_charger: bool = False
    notes: Optional[str] = Field(
        None, description="Any custom context that should show up in the narrative"
    )

    @validator("built_year")
    def validate_built_year(cls, value: int) -> int:
        if value > 2050:
            raise ValueError("built_year must be in the past")
        return value


class HomeQuestRequest(BaseModel):
    """Input payload for generating a HomeQuest plan."""

    home: HomeProfile
    goals: List[GoalType] = Field(
        default_factory=lambda: [GoalType.LOWER_BILLS],
        description="Priority focus areas for the homeowner",
    )
    annual_budget: Optional[PositiveFloat] = Field(
        None,
        description="If supplied, used to right-size the phased recommendations",
    )
    preferred_timeline_months: Optional[PositiveInt] = Field(
        None, description="Ideal completion timeframe used for narrative guidance"
    )


class GoalDefinition(BaseModel):
    """Metadata describing what each goal means."""

    goal: GoalType
    title: str
    description: str
    success_indicators: List[str]


class ScoreCard(BaseModel):
    """Summarises the energy performance trajectory."""

    baseline_score: int = Field(..., ge=0, le=100)
    target_score: int = Field(..., ge=0, le=100)
    estimated_annual_savings: float = Field(..., ge=0)
    carbon_reduction_tonnes: float = Field(..., ge=0)


class UpgradeAction(BaseModel):
    """Concrete step recommended for the homeowner."""

    id: str
    title: str
    description: str
    impact_level: str
    difficulty: str
    estimated_cost: float = Field(..., ge=0)
    estimated_annual_savings: float = Field(..., ge=0)
    incentives: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class ImplementationPhase(BaseModel):
    """Outlines how actions roll out over time."""

    name: str
    timeframe: str
    focus: str
    actions: List[str]


class FinancingOption(BaseModel):
    """Suggested pathways to pay for upgrades."""

    name: str
    description: str
    option_type: str
    eligibility: str


class HomeSummary(BaseModel):
    """Highlights of the existing home profile pulled into the plan."""

    property_name: str
    location: str
    size_sq_ft: int
    build_vintage: str
    current_systems: Dict[str, str]
    narrative_highlights: List[str]


class HomeQuestPlan(BaseModel):
    """Full response returned to clients after running the planner."""

    plan_id: str
    home_summary: HomeSummary
    scorecard: ScoreCard
    priority_actions: List[UpgradeAction]
    phased_timeline: List[ImplementationPhase]
    financing: List[FinancingOption]
    narrative: str

