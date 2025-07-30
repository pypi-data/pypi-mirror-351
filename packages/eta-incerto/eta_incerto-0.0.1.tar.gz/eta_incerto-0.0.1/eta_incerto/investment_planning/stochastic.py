import dataclasses

import pyomo.environ as pyo

from eta_incerto.investment_planning.base import Scenario, ScenarioCollection, UncertaintyFramework


@dataclasses.dataclass
class StochasticScenario(Scenario):
    probability: float


class StochasticScenarioCollection(ScenarioCollection):
    _scenario_type = StochasticScenario

    def set_scenario(self, scenario: _scenario_type):
        super().set_scenario(scenario)

    def get_scenario(self, name: str) -> _scenario_type:
        return super().get_scenario(name)


class StochasticFramework(UncertaintyFramework):
    def __init__(self, scenarios: StochasticScenarioCollection):
        super().__init__(scenarios)

    def build_model(self, solver: str = "cplex"):
        self._global_model = global_model = pyo.ConcreteModel()
        global_model.scenarios = pyo.Block()

        global_objective = 0
        for scenario_name in self._scenarios.names():
            scenario = self._scenarios.get_scenario(scenario_name)
            scenario.system._join_models()
            scenario.system.objective.construct_objective()
            global_objective += scenario.probability * scenario.system.objective.function
            scenario.system.objective.deactivate()

            global_model.scenarios.add_component(scenario_name, pyo.Block())
            global_model.scenarios.component(scenario_name).add_component("submodel", scenario.system.model)

        global_model.objective = pyo.Objective(expr=global_objective, sense=pyo.minimize)

        self._equate_investment_decisions_across_submodels(global_model, global_model.scenarios)

    def objective_value(self):
        return self._global_model.objective()

    def submodel(self, name: str) -> pyo.Block:
        return self._global_model.local_scenarios[name]
