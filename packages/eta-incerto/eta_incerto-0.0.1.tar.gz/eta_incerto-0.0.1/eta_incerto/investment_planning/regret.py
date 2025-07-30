from __future__ import annotations

import logging

import pyomo.environ as pyo

from eta_incerto.investment_planning.base import ScenarioCollection, UncertaintyFramework

logger = logging.getLogger(__name__)


class RegretFramework(UncertaintyFramework):
    def __init__(self, scenarios: ScenarioCollection):
        super().__init__(scenarios)

    def build_model(self, tee: bool = False, options: dict | None = None):
        if options is None:
            options = {}
        solver_name = options.pop("solver", "cplex")

        self._global_model = global_model = pyo.ConcreteModel()
        global_model.scenarios = pyo.Block()
        global_model.worst_objective_delta = pyo.Var()

        for scenario_name in self._scenarios.names():
            logger.info("Finished calculating optimal solution for base scenario %s.", scenario_name)
            scenario = self._scenarios.get_scenario(scenario_name)
            scenario.system.solve(solver=solver_name, tee=tee, options=options)
            logger.info("Finished calculating optimal solution for base scenario %s.", scenario_name)
            ideal_objective = pyo.value(scenario.system.objective)

            regret_constraint = pyo.Constraint(
                rule=global_model.worst_objective_delta >= scenario.system.objective.function - ideal_objective
            )
            scenario.system.objective.deactivate()

            global_model.scenarios.add_component(scenario_name, pyo.Block())
            global_model.scenarios.component(scenario_name).add_component("submodel", scenario.system.model)
            global_model.scenarios.component(scenario_name).add_component("regret_constraint", regret_constraint)

        logger.info("Finished calculation of all base scenarios.")

        global_model.objective = pyo.Objective(rule=global_model.worst_objective_delta, sense=pyo.minimize)
        logger.info("Set objective for regret optimization.")

        self._equate_investment_decisions_across_submodels(global_model, global_model.scenarios)
