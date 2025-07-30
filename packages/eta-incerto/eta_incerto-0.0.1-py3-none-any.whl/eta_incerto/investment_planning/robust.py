import pyomo.environ as pyo

from eta_incerto.investment_planning.base import ScenarioCollection, UncertaintyFramework


class RobustFramework(UncertaintyFramework):
    def __init__(self, scenarios: ScenarioCollection):
        super().__init__(scenarios)

    def build_model(self):
        self._global_model = global_model = pyo.ConcreteModel()
        global_model.scenarios = pyo.Block()
        global_model.worst_objective = pyo.Var()
        for scenario_name in self._scenarios.names():
            scenario = self._scenarios.get_scenario(scenario_name)
            scenario.system._join_models()
            scenario.system.objective.construct_objective()
            robust_constraint = pyo.Constraint(rule=global_model.worst_objective >= scenario.system.objective.function)
            scenario.system.objective.deactivate()

            global_model.scenarios.add_component(scenario_name, pyo.Block())
            global_model.scenarios.component(scenario_name).add_component("submodel", scenario.system.model)
            global_model.scenarios.component(scenario_name).add_component("robust_constraint", robust_constraint)

        global_model.objective = pyo.Objective(rule=global_model.worst_objective, sense=pyo.minimize)

        self._equate_investment_decisions_across_submodels(global_model, global_model.scenarios)
