"""Domain logic for creating HomeQuest retrofit roadmaps."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

from ..schemas.homequest import (
    FinancingOption,
    GoalDefinition,
    GoalType,
    HomeProfile,
    HomeQuestPlan,
    HomeQuestRequest,
    HomeSummary,
    ImplementationPhase,
    InsulationLevel,
    ScoreCard,
    UpgradeAction,
)


@dataclass(frozen=True)
class _GoalInfo:
    """Internal representation of a HomeQuest goal."""

    definition: GoalDefinition
    score_boost: int
    narrative: str


@dataclass(frozen=True)
class _ActionTemplate:
    """Configuration used to build an upgrade recommendation."""

    id: str
    title: str
    description: str
    impact_level: str
    difficulty: str
    base_cost: float
    base_savings: float
    incentives: Sequence[str]
    dependencies: Sequence[str]
    applies: Callable[[HomeProfile, HomeQuestRequest], bool]
    goal_weights: Dict[GoalType, int]

    def priority_weight(self, goals: Iterable[GoalType]) -> float:
        weight = 1.0
        for goal in goals:
            weight += self.goal_weights.get(goal, 0)
        if self.impact_level == "high":
            weight += 0.75
        elif self.impact_level == "medium":
            weight += 0.25
        return weight

    def build_action(self, home: HomeProfile) -> UpgradeAction:
        scale = max(0.6, min(1.6, home.square_feet / 2000))
        return UpgradeAction(
            id=self.id,
            title=self.title,
            description=self.description,
            impact_level=self.impact_level,
            difficulty=self.difficulty,
            estimated_cost=round(self.base_cost * scale, 2),
            estimated_annual_savings=round(self.base_savings * scale, 2),
            incentives=list(self.incentives),
            dependencies=list(self.dependencies),
        )


class HomeQuestPlanner:
    """Generates decarbonisation pathways for a single residence."""

    def __init__(self) -> None:
        self._plans: Dict[str, HomeQuestPlan] = {}
        self._goal_library: Dict[GoalType, _GoalInfo] = self._build_goal_library()
        self._action_templates: List[_ActionTemplate] = self._build_action_templates()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_goal_definitions(self) -> List[GoalDefinition]:
        """Return the configured goal catalogue."""

        return [info.definition for info in self._goal_library.values()]

    def create_plan(self, request: HomeQuestRequest) -> HomeQuestPlan:
        """Build a fully-populated HomeQuest plan from the provided request."""

        plan_id = str(uuid.uuid4())
        baseline_score = self._compute_baseline_score(request.home)
        target_score = min(98, baseline_score + self._score_boost_for_goals(request.goals))
        estimated_savings, carbon_reduction = self._estimate_savings_and_carbon(
            request.home.average_monthly_bill, baseline_score, target_score
        )

        actions = self._determine_actions(request)
        timeline = self._build_timeline(actions)
        financing = self._financing_options(request, actions)

        plan = HomeQuestPlan(
            plan_id=plan_id,
            home_summary=self._summarise_home(request),
            scorecard=ScoreCard(
                baseline_score=baseline_score,
                target_score=target_score,
                estimated_annual_savings=round(estimated_savings, 2),
                carbon_reduction_tonnes=round(carbon_reduction, 2),
            ),
            priority_actions=actions,
            phased_timeline=timeline,
            financing=financing,
            narrative=self._create_narrative(request, actions, target_score),
        )

        self._plans[plan_id] = plan
        return plan

    def fetch_plan(self, plan_id: str) -> HomeQuestPlan:
        """Retrieve a previously generated plan."""

        if plan_id not in self._plans:
            raise KeyError(f"Plan with id {plan_id} not found")
        return self._plans[plan_id]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_goal_library(self) -> Dict[GoalType, _GoalInfo]:
        return {
            GoalType.LOWER_BILLS: _GoalInfo(
                definition=GoalDefinition(
                    goal=GoalType.LOWER_BILLS,
                    title="Lower monthly bills",
                    description="Identify envelope and equipment upgrades that shrink utility spend.",
                    success_indicators=[
                        "15% reduction in annual energy cost",
                        "Measured reduction in air leakage",
                        "Efficient HVAC matched to home load",
                    ],
                ),
                score_boost=8,
                narrative="The roadmap targets measures that reliably trim ongoing utility costs.",
            ),
            GoalType.COMFORT: _GoalInfo(
                definition=GoalDefinition(
                    goal=GoalType.COMFORT,
                    title="Improve comfort",
                    description="Promote even temperatures, balanced ventilation, and quieter operation.",
                    success_indicators=[
                        "Room-to-room temperature swings under 2°F",
                        "Continuous balanced ventilation",
                        "Reduced equipment cycling noise",
                    ],
                ),
                score_boost=6,
                narrative="Comfort-focused measures keep temperatures stable and ventilation balanced.",
            ),
            GoalType.RESILIENCE: _GoalInfo(
                definition=GoalDefinition(
                    goal=GoalType.RESILIENCE,
                    title="Build resilience",
                    description="Add backup capacity and load management for outages or peak events.",
                    success_indicators=[
                        "Critical loads supported for at least 8 hours",
                        "Ability to island with storage or generator",
                        "Automated load shedding during grid events",
                    ],
                ),
                score_boost=5,
                narrative="Resilience upgrades make sure critical circuits stay online during disruptions.",
            ),
            GoalType.DECARBONIZE: _GoalInfo(
                definition=GoalDefinition(
                    goal=GoalType.DECARBONIZE,
                    title="Decarbonise the property",
                    description="Electrify major loads and prepare for clean onsite generation.",
                    success_indicators=[
                        "Space and water heating delivered by electric equipment",
                        "Electrical system sized for renewable capacity",
                        "Documented decline in emissions year over year",
                    ],
                ),
                score_boost=7,
                narrative="Electrification and solar readiness move the home toward low-carbon operations.",
            ),
            GoalType.ELECTRIFY: _GoalInfo(
                definition=GoalDefinition(
                    goal=GoalType.ELECTRIFY,
                    title="Electrify appliances",
                    description="Swap fossil-fuel appliances for efficient electric alternatives.",
                    success_indicators=[
                        "Combustion appliances replaced with heat pump technology",
                        "Panel capacity available for new loads",
                        "Charging infrastructure ready for EV adoption",
                    ],
                ),
                score_boost=6,
                narrative="Panel and appliance upgrades unlock an all-electric home footprint.",
            ),
        }

    def _build_action_templates(self) -> List[_ActionTemplate]:
        return [
            _ActionTemplate(
                id="envelope-upgrade",
                title="Seal leaks and add insulation",
                description="Air seal the envelope and top up attic insulation to cut infiltration.",
                impact_level="high",
                difficulty="moderate",
                base_cost=3200,
                base_savings=260,
                incentives=("IRA 25C insulation tax credit",),
                dependencies=(),
                applies=lambda home, _req: home.insulation_level != InsulationLevel.GOOD,
                goal_weights={
                    GoalType.LOWER_BILLS: 3,
                    GoalType.COMFORT: 2,
                },
            ),
            _ActionTemplate(
                id="heat-pump",
                title="Install high-efficiency heat pump",
                description="Replace legacy fossil systems with a variable-speed cold-climate heat pump.",
                impact_level="high",
                difficulty="high",
                base_cost=9600,
                base_savings=410,
                incentives=("Federal heat pump tax credit",),
                dependencies=("envelope-upgrade",),
                applies=lambda home, req: "heat pump" not in home.hvac_type.lower()
                or GoalType.ELECTRIFY in req.goals,
                goal_weights={
                    GoalType.DECARBONIZE: 3,
                    GoalType.ELECTRIFY: 4,
                    GoalType.LOWER_BILLS: 1,
                },
            ),
            _ActionTemplate(
                id="panel-upgrade",
                title="Expand electrical panel capacity",
                description="Upgrade service panel and add dedicated circuits for future electric loads.",
                impact_level="medium",
                difficulty="high",
                base_cost=3400,
                base_savings=70,
                incentives=("Utility make-ready rebate",),
                dependencies=(),
                applies=lambda home, req: home.has_ev_charger or GoalType.ELECTRIFY in req.goals,
                goal_weights={
                    GoalType.ELECTRIFY: 3,
                    GoalType.RESILIENCE: 1,
                },
            ),
            _ActionTemplate(
                id="balanced-ventilation",
                title="Install balanced ventilation",
                description="Add an energy recovery ventilator with smart controls for humidity balance.",
                impact_level="medium",
                difficulty="moderate",
                base_cost=4700,
                base_savings=110,
                incentives=("Ventilation equipment credit",),
                dependencies=(),
                applies=lambda _home, req: GoalType.COMFORT in req.goals,
                goal_weights={
                    GoalType.COMFORT: 4,
                    GoalType.RESILIENCE: 1,
                },
            ),
            _ActionTemplate(
                id="solar-ready",
                title="Prepare for rooftop solar",
                description="Run conduit, reserve wall space, and ready the roof for solar and storage.",
                impact_level="medium",
                difficulty="moderate",
                base_cost=4100,
                base_savings=160,
                incentives=("30% Investment Tax Credit",),
                dependencies=(),
                applies=lambda home, req: not home.has_rooftop_solar
                and GoalType.DECARBONIZE in req.goals,
                goal_weights={
                    GoalType.DECARBONIZE: 3,
                    GoalType.RESILIENCE: 2,
                },
            ),
            _ActionTemplate(
                id="resilience-kit",
                title="Add critical load backup kit",
                description="Pair smart load management with storage-ready inverter for outages.",
                impact_level="medium",
                difficulty="moderate",
                base_cost=7200,
                base_savings=80,
                incentives=("Virtual power plant revenue opportunities",),
                dependencies=("solar-ready",),
                applies=lambda _home, req: GoalType.RESILIENCE in req.goals,
                goal_weights={
                    GoalType.RESILIENCE: 4,
                },
            ),
            _ActionTemplate(
                id="diagnostic-audit",
                title="Complete diagnostic energy audit",
                description="Deploy smart monitoring and load calculations to sequence retrofits.",
                impact_level="medium",
                difficulty="low",
                base_cost=650,
                base_savings=75,
                incentives=(),
                dependencies=(),
                applies=lambda _home, _req: True,
                goal_weights={},
            ),
        ]

    def _score_boost_for_goals(self, goals: Iterable[GoalType]) -> int:
        base = 10
        for goal in goals:
            info = self._goal_library.get(goal)
            if info:
                base += info.score_boost
        return min(base, 32)

    def _compute_baseline_score(self, home: HomeProfile) -> int:
        current_year = date.today().year
        score = 75

        age_penalty = max(0, (current_year - home.built_year) // 15)
        score -= min(age_penalty * 2, 18)

        if home.insulation_level == InsulationLevel.POOR:
            score -= 12
        elif home.insulation_level == InsulationLevel.AVERAGE:
            score -= 5

        hvac = home.hvac_type.lower()
        if "furnace" in hvac or "boiler" in hvac:
            score -= 6
        elif "heat pump" in hvac:
            score += 4

        if not home.has_rooftop_solar:
            score -= 2

        return max(30, min(score, 90))

    def _estimate_savings_and_carbon(
        self, monthly_bill: float, baseline_score: int, target_score: int
    ) -> Tuple[float, float]:
        annual_bill = monthly_bill * 12
        improvement_ratio = max(target_score - baseline_score, 0) / 100
        estimated_savings = annual_bill * (0.1 + improvement_ratio * 0.4)
        carbon_reduction = estimated_savings * 0.00045 * 12
        return estimated_savings, carbon_reduction

    def _determine_actions(self, request: HomeQuestRequest) -> List[UpgradeAction]:
        home = request.home
        ranked: List[Tuple[float, UpgradeAction]] = []
        for template in self._action_templates:
            if template.applies(home, request):
                weight = template.priority_weight(request.goals)
                ranked.append((weight, template.build_action(home)))

        if not ranked:
            ranked.append((1.0, self._action_templates[-1].build_action(home)))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [action for _weight, action in ranked]

    def _build_timeline(self, actions: List[UpgradeAction]) -> List[ImplementationPhase]:
        if not actions:
            return []

        phases: List[ImplementationPhase] = []
        first_wave = [action.title for action in actions[:2]]
        phases.append(
            ImplementationPhase(
                name="Kickoff",
                timeframe="0-6 months",
                focus="Start with audits and quick efficiency wins",
                actions=first_wave,
            )
        )

        if len(actions) > 2:
            middle = [action.title for action in actions[2:5]]
            phases.append(
                ImplementationPhase(
                    name="Deep retrofits",
                    timeframe="6-18 months",
                    focus="Schedule mechanical upgrades and ventilation improvements",
                    actions=middle,
                )
            )

        if len(actions) > 5:
            later = [action.title for action in actions[5:]]
            phases.append(
                ImplementationPhase(
                    name="Future readiness",
                    timeframe="18-30 months",
                    focus="Layer in resilience and renewable integration projects",
                    actions=later,
                )
            )

        return phases

    def _financing_options(
        self, request: HomeQuestRequest, actions: List[UpgradeAction]
    ) -> List[FinancingOption]:
        annual_budget = request.annual_budget or 10000
        total_cost = sum(action.estimated_cost for action in actions)

        options: List[FinancingOption] = [
            FinancingOption(
                name="Inflation Reduction Act incentives",
                description="Combine 25C tax credits with local rebates to offset upfront costs.",
                option_type="incentive",
                eligibility="Owner-occupied residences installing qualifying equipment",
            ),
            FinancingOption(
                name="Green loan partners",
                description="Credit unions and CDFIs offer low-interest financing for energy projects.",
                option_type="loan",
                eligibility="Borrowers with credit score 640+ and clear retrofit scope",
            ),
        ]

        if total_cost > annual_budget:
            options.append(
                FinancingOption(
                    name="PACE or on-bill financing",
                    description="Repay upgrades over time through property taxes or utility billing.",
                    option_type="financing",
                    eligibility="Property taxes current and recent energy audit on file",
                )
            )
        else:
            options.append(
                FinancingOption(
                    name="Pay-as-you-save",
                    description="Phase work to stay within available cash flow while capturing incentives.",
                    option_type="cash-flow",
                    eligibility=f"Projects under ${annual_budget:,.0f} in annual spend",
                )
            )

        return options

    def _summarise_home(self, request: HomeQuestRequest) -> HomeSummary:
        home = request.home
        highlights = [
            f"{home.square_feet:,} sq ft {home.occupancy_type.value.replace('_', ' ')}",
            f"Average bill ${home.average_monthly_bill:,.0f}/month",
            f"Primary HVAC: {home.hvac_type}",
        ]
        if home.notes:
            highlights.append(home.notes)

        current_systems = {
            "HVAC": home.hvac_type,
            "Water Heating": home.water_heater or "unspecified",
            "Solar": "Installed" if home.has_rooftop_solar else "Not installed",
        }

        return HomeSummary(
            property_name=home.name,
            location=f"{home.city}, {home.state}",
            size_sq_ft=home.square_feet,
            build_vintage=f"Built in {home.built_year}",
            current_systems=current_systems,
            narrative_highlights=highlights,
        )

    def _create_narrative(
        self, request: HomeQuestRequest, actions: List[UpgradeAction], target_score: int
    ) -> str:
        home = request.home
        sentences = [
            (
                f"HomeQuest analysed {home.name} in {home.city}, {home.state} and mapped a "
                f"pathway to reach a score of {target_score}."
            )
        ]

        if request.preferred_timeline_months:
            sentences.append(
                f"The timeline is paced to finish within {request.preferred_timeline_months} months."
            )

        for goal in request.goals:
            info = self._goal_library.get(goal)
            if info:
                sentences.append(info.narrative)

        if actions:
            lead = actions[0]
            sentences.append(
                f"The first priority is {lead.title.lower()} with estimated annual savings of "
                f"${lead.estimated_annual_savings:,.0f}."
            )

        sentences.append(
            "Plans remain stored so homeowners can revisit recommendations as incentives evolve."
        )

        return " ".join(sentences)


planner = HomeQuestPlanner()
