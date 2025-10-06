"""Domain logic for creating HomeQuest retrofit roadmaps."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from ..schemas.homequest import (
    FinancingOption,
    GoalDefinition,
    GoalType,
    HomeQuestPlan,
    HomeQuestRequest,
    HomeSummary,
    ImplementationPhase,
    InsulationLevel,
    ScoreCard,
    UpgradeAction,
)


@dataclass(frozen=True)
class _GoalDescriptor:
    """Internal representation of each HomeQuest goal."""

    definition: GoalDefinition
    bonus_score: int
    narrative_hook: str


class HomeQuestPlanner:
    """Generates decarbonisation pathways for a single residence."""

    def __init__(self) -> None:
        self._plans: Dict[str, HomeQuestPlan] = {}
        self._goal_library: Dict[GoalType, _GoalDescriptor] = {
            GoalType.LOWER_BILLS: _GoalDescriptor(
                definition=GoalDefinition(
                    goal=GoalType.LOWER_BILLS,
                    title="Slash monthly utility bills",
                    description=(
                        "Reduce wasted energy through envelope sealing, smart controls, "
                        "and high-efficiency equipment upgrades."
                    ),
                    success_indicators=[
                        "15%+ reduction in annual energy spend",
                        "Tighter building envelope (ACH50 < 5)",
                        "Right-sized HVAC systems matched to load"
                    ],
                ),
                bonus_score=8,
                narrative_hook=(
                    "Right-sizing equipment and cutting air leakage creates predictable, "
                    "lower energy bills year-round."
                ),
            ),
            GoalType.COMFORT: _GoalDescriptor(
                definition=GoalDefinition(
                    goal=GoalType.COMFORT,
                    title="Elevate comfort",
                    description=(
                        "Focus on steady indoor temperatures, healthy ventilation, and "
                        "draft-free rooms."
                    ),
                    success_indicators=[
                        "Consistent room-to-room temperatures",
                        "Balanced humidity through ventilation",
                        "Reduced noise from mechanical systems",
                    ],
                ),
                bonus_score=5,
                narrative_hook="Air sealing and variable-speed systems stabilise comfort without spikes in usage.",
            ),
            GoalType.RESILIENCE: _GoalDescriptor(
                definition=GoalDefinition(
                    goal=GoalType.RESILIENCE,
                    title="Boost resilience",
                    description=(
                        "Plan for backup power, grid flexibility, and the ability to ride out disruptions."
                    ),
                    success_indicators=[
                        "At least one day of critical load coverage",
                        "Ability to island with solar or battery backup",
                        "Active load management for peak demand",
                    ],
                ),
                bonus_score=4,
                narrative_hook="Solar-ready wiring and storage-ready panels support resilience upgrades later on.",
            ),
            GoalType.DECARBONIZE: _GoalDescriptor(
                definition=GoalDefinition(
                    goal=GoalType.DECARBONIZE,
                    title="Decarbonise the property",
                    description=(
                        "Electrify end uses, integrate renewables, and shrink total carbon emissions."
                    ),
                    success_indicators=[
                        "100% electric space and water heating",
                        "Grid-supplied energy from renewable sources",
                        "Verified greenhouse gas reduction year-over-year",
                    ],
                ),
                bonus_score=7,
                narrative_hook="Electrification prepares the home for clean power while shrinking emissions.",
            ),
            GoalType.ELECTRIFY: _GoalDescriptor(
                definition=GoalDefinition(
                    goal=GoalType.ELECTRIFY,
                    title="Electrify everything",
                    description="Transition off fossil-fuel appliances with high efficiency electric alternatives.",
                    success_indicators=[
                        "Dual-fuel or fossil appliances replaced with heat pump technology",
                        "Electrical panel has capacity for new loads",
                        "EV-ready outlet accessible on-site",
                    ],
                ),
                bonus_score=6,
                narrative_hook="Panel upgrades and heat pump technology unlock all-electric living.",
            ),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_goal_definitions(self) -> List[GoalDefinition]:
        """Return the configured goal catalogue."""

        return [descriptor.definition for descriptor in self._goal_library.values()]

    def create_plan(self, request: HomeQuestRequest) -> HomeQuestPlan:
        """Build a fully-populated HomeQuest plan from the provided request."""

        plan_id = str(uuid.uuid4())
        baseline_score = self._compute_baseline_score(request)
        target_score = min(95, baseline_score + self._score_boost_for_goals(request.goals))
        estimated_savings, carbon_reduction = self._estimate_savings_and_carbon(request, target_score)

        actions = self._determine_actions(request, baseline_score)
        timeline = self._build_timeline(actions)
        financing = self._financing_options(request)

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
    def _score_boost_for_goals(self, goals: Iterable[GoalType]) -> int:
        bonus = 10  # baseline improvement expectation even with a single goal
        for goal in goals:
            descriptor = self._goal_library.get(goal)
            if descriptor:
                bonus += descriptor.bonus_score
        return min(bonus, 35)

    def _compute_baseline_score(self, request: HomeQuestRequest) -> int:
        home = request.home
        score = 78

        age_penalty = max(0, (2024 - home.built_year) // 20)
        score -= min(age_penalty * 2, 20)

        if home.insulation_level == InsulationLevel.POOR:
            score -= 12
        elif home.insulation_level == InsulationLevel.AVERAGE:
            score -= 4

        if "furnace" in home.hvac_type.lower():
            score -= 6
        if "window" in home.hvac_type.lower():
            score -= 4
        if "heat pump" in home.hvac_type.lower():
            score += 5

        if not home.has_rooftop_solar:
            score -= 2

        score = max(35, min(score, 88))
        return score

    def _estimate_savings_and_carbon(
        self, request: HomeQuestRequest, target_score: int
    ) -> Tuple[float, float]:
        monthly_bill = request.home.average_monthly_bill
        savings_ratio = max(0.12, min(0.32, (target_score - 50) / 200))
        estimated_annual_savings = monthly_bill * 12 * savings_ratio
        carbon_reduction = estimated_annual_savings / 1000 * 0.5
        return estimated_annual_savings, carbon_reduction

    def _determine_actions(
        self, request: HomeQuestRequest, baseline_score: int
    ) -> List[UpgradeAction]:
        home = request.home
        actions: List[UpgradeAction] = []

        def add_action(action: UpgradeAction) -> None:
            actions.append(action)

        sq_ft_factor = home.square_feet / 2000

        # Envelope upgrades
        if home.insulation_level in {InsulationLevel.POOR, InsulationLevel.AVERAGE}:
            add_action(
                UpgradeAction(
                    id="envelope-upgrade",
                    title="Seal and insulate the envelope",
                    description=(
                        "Comprehensive blower-door guided air sealing, attic insulation "
                        "top-up, and rim joist treatment to slash infiltration."
                    ),
                    impact_level="high",
                    difficulty="moderate",
                    estimated_cost=3500 * sq_ft_factor,
                    estimated_annual_savings=max(180.0, 280.0 * sq_ft_factor),
                    incentives=[
                        "IRA Section 25C insulation tax credit",
                        "DCSEU Home Performance rebates",
                    ],
                )
            )

        if "furnace" in home.hvac_type.lower() or GoalType.ELECTRIFY in request.goals:
            add_action(
                UpgradeAction(
                    id="heat-pump",
                    title="Install cold-climate heat pump",
                    description=(
                        "Replace aging fossil systems with a variable-speed cold-climate "
                        "heat pump sized via Manual J to maintain comfort down to 5°F."
                    ),
                    impact_level="high",
                    difficulty="high",
                    estimated_cost=9800 * sq_ft_factor,
                    estimated_annual_savings=max(320.0, 420.0 * sq_ft_factor),
                    incentives=[
                        "Federal 25C heat pump credit",
                        "Utility demand response enrollment bonus",
                    ],
                    dependencies=["envelope-upgrade"],
                )
            )

        if not home.has_rooftop_solar and GoalType.DECARBONIZE in request.goals:
            add_action(
                UpgradeAction(
                    id="solar-ready",
                    title="Prepare for rooftop solar + storage",
                    description=(
                        "Upgrade electrical panel, run conduit to roof, and reserve wall "
                        "space for a future battery to enable net-zero capability."
                    ),
                    impact_level="medium",
                    difficulty="moderate",
                    estimated_cost=4200,
                    estimated_annual_savings=150.0,
                    incentives=[
                        "30% Investment Tax Credit",
                        "Solar Renewable Energy Credit (SREC) revenue",
                    ],
                )
            )

        if GoalType.RESILIENCE in request.goals:
            add_action(
                UpgradeAction(
                    id="resilience-package",
                    title="Critical load resilience kit",
                    description=(
                        "Pair smart panel monitoring with a hybrid inverter and small "
                        "battery to back up refrigeration, medical devices, and Wi-Fi."
                    ),
                    impact_level="medium",
                    difficulty="moderate",
                    estimated_cost=7500,
                    estimated_annual_savings=80.0,
                    incentives=["Grid service revenue through VPP programs"],
                    dependencies=["solar-ready"],
                )
            )

        if GoalType.COMFORT in request.goals:
            add_action(
                UpgradeAction(
                    id="ventilation-upgrade",
                    title="Add balanced ventilation + smart controls",
                    description=(
                        "Install an Energy Recovery Ventilator with smart, room-based "
                        "controls to balance humidity and fresh air."
                    ),
                    impact_level="medium",
                    difficulty="moderate",
                    estimated_cost=4800,
                    estimated_annual_savings=95.0,
                    incentives=["IRA ventilation equipment credit"],
                )
            )

        if home.has_ev_charger or GoalType.ELECTRIFY in request.goals:
            add_action(
                UpgradeAction(
                    id="panel-upgrade",
                    title="Upgrade electrical panel + circuits",
                    description=(
                        "Expand service panel to 200A, add dedicated EV-ready circuit, "
                        "and install monitoring to track new loads."
                    ),
                    impact_level="medium",
                    difficulty="high",
                    estimated_cost=3600,
                    estimated_annual_savings=65.0,
                    incentives=["Utility EV charger make-ready rebate"],
                )
            )

        if not actions:
            add_action(
                UpgradeAction(
                    id="smart-audit",
                    title="Comprehensive smart energy audit",
                    description=(
                        "Benchmark the property with smart sensors, load disaggregation, "
                        "and a Manual J load calc to confirm next retrofit steps."
                    ),
                    impact_level="medium",
                    difficulty="low",
                    estimated_cost=750,
                    estimated_annual_savings=80.0,
                )
            )

        # Prioritise by impact first, then savings.
        actions.sort(
            key=lambda action: (
                0 if action.impact_level == "high" else 1,
                -action.estimated_annual_savings,
            )
        )

        return actions

    def _build_timeline(self, actions: List[UpgradeAction]) -> List[ImplementationPhase]:
        if not actions:
            return []

        phases: List[ImplementationPhase] = []

        # Phase 1: first two actions
        first_actions = [action.title for action in actions[:2]]
        phases.append(
            ImplementationPhase(
                name="Stabilise & Audit",
                timeframe="0-3 months",
                focus="Knock out diagnostics and quick envelope wins",
                actions=first_actions,
            )
        )

        if len(actions) > 2:
            mid_actions = [action.title for action in actions[2:4]]
            phases.append(
                ImplementationPhase(
                    name="Deep Retrofit",
                    timeframe="4-12 months",
                    focus="Tackle HVAC and ventilation upgrades with contractors",
                    actions=mid_actions,
                )
            )

        if len(actions) > 4:
            remaining = [action.title for action in actions[4:]]
            phases.append(
                ImplementationPhase(
                    name="Future Proof",
                    timeframe="12-24 months",
                    focus="Layer on resilience, solar, and smart load management",
                    actions=remaining,
                )
            )

        return phases

    def _financing_options(self, request: HomeQuestRequest) -> List[FinancingOption]:
        annual_budget = request.annual_budget or 10000
        options: List[FinancingOption] = [
            FinancingOption(
                name="Inflation Reduction Act incentives",
                description=(
                    "Stack 25C tax credits for heat pumps, insulation, and ventilation with "
                    "state-level rebates to offset upfront costs."
                ),
                option_type="incentive",
                eligibility="Owner-occupied primary residence with qualifying equipment",
            ),
            FinancingOption(
                name="On-bill repayment or PACE",
                description=(
                    "Finance deeper retrofits through Property Assessed Clean Energy or "
                    "utility on-bill tariffs, keeping payments neutral to savings."
                ),
                option_type="financing",
                eligibility="Property tax current, energy audit completed in last 24 months",
            ),
            FinancingOption(
                name="Green lending partners",
                description=(
                    "Mission-driven credit unions offer low-interest loans for projects "
                    "with clear comfort and health benefits."
                ),
                option_type="loan",
                eligibility="Budget need above ${:,.0f} with credit score 640+".format(annual_budget),
            ),
        ]
        return options

    def _summarise_home(self, request: HomeQuestRequest) -> HomeSummary:
        home = request.home
        location = f"{home.city}, {home.state}"
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
            location=location,
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
                f"pathway to lift the efficiency score to {target_score}."
            )
        ]

        if request.preferred_timeline_months:
            sentences.append(
                f"The phased roadmap is tuned to finish within {request.preferred_timeline_months} months."
            )

        for goal in request.goals:
            descriptor = self._goal_library.get(goal)
            if descriptor:
                sentences.append(descriptor.narrative_hook)

        if actions:
            top_action = actions[0]
            sentences.append(
                f"The first priority is {top_action.title.lower()} delivering roughly "
                f"${top_action.estimated_annual_savings:,.0f} in annual savings."
            )

        sentences.append(
            "HomeQuest keeps progress stored with this plan so the homeowner can revisit "
            "and refresh recommendations as new incentives roll out."
        )

        return " " .join(sentences)


planner = HomeQuestPlanner()

