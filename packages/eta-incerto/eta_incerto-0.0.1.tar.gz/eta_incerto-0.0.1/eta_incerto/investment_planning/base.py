from __future__ import annotations

import abc
import dataclasses
import logging
import warnings
from abc import ABC
from collections.abc import Iterable

import eta_components.milp_component_library as mcl
import pyomo.environ as pyo

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Scenario:
    name: str
    system: mcl.types.System


class ScenarioCollection:
    _scenario_type = Scenario

    def __init__(self, scenarios: Iterable[_scenario_type] | None = None):
        self._scenarios: dict[str, Scenario] = {}
        if scenarios is not None:
            for scenario in scenarios:
                self.set_scenario(scenario)

    def set_scenario(self, scenario: _scenario_type):
        if scenario.name in self._scenarios:
            warnings.warn(f"Overwriting scenario {scenario.name}.", stacklevel=2)
        self._scenarios[scenario.name] = scenario

    def get_scenario(self, name: str) -> _scenario_type:
        if name not in self._scenarios:
            raise KeyError(f"No scenario of name {name}.")
        return self._scenarios[name]

    def names(self) -> dict.keys:
        return self._scenarios.keys()


class UncertaintyFramework(ABC):
    def __init__(self, scenarios: ScenarioCollection):
        self._scenarios: ScenarioCollection = scenarios
        self._first_stage_variables: dict = {}
        self._global_model: pyo.ConcreteModel = pyo.ConcreteModel()

    @abc.abstractmethod
    def build_model(self):
        """"""

    def solve(self, tee: bool = False, options: dict | None = None):
        if options is None:
            options = {}

        solver_name = options.pop("solver", "cplex")
        solver = pyo.SolverFactory(solver_name)
        if options:
            solver.options = options
        solver.solve(self._global_model, tee=tee)

    def _equate_investment_decisions_across_submodels(
        self, global_model: pyo.ConcreteModel, scenarios_block: pyo.Block
    ):
        submodel_first_stage_variables = self._extract_first_stage_variables_from_submodels()

        self._check_all_submodels_have_same_first_stage_variables(submodel_first_stage_variables)

        self._first_stage_variables = self._create_global_first_stage_variables(
            global_model, submodel_first_stage_variables
        )

        self._equate_global_first_stage_variables_to_submodel_first_stage_variables(
            scenarios_block, self._first_stage_variables, submodel_first_stage_variables
        )
        logger.info("Equated the investment decisions across all base scenarios.")

    def _extract_first_stage_variables_from_submodels(self):
        # TODO(#1): Add p_out_nom for all unit classes (storage and HEX)
        submodel_first_stage_variables = {}
        for scenario_name in self._scenarios.names():
            submodel_first_stage_variables[scenario_name] = {
                f"{unit.name}.{unit.model.p_out_nom.local_name}": unit.model.p_out_nom
                for unit in self._scenarios.get_scenario(scenario_name).system.units
                if unit.has_investment_decision()
            }
        return submodel_first_stage_variables

    def _check_all_submodels_have_same_first_stage_variables(
        self, submodel_first_stage_variables: dict[str, dict[str, pyo.Var]]
    ):
        first_scenario_name = self.__name_of_first_scenario()
        for scenario_name in self._scenarios.names():
            if (
                not submodel_first_stage_variables[first_scenario_name].keys()
                == submodel_first_stage_variables[scenario_name].keys()
            ):
                raise ValueError(
                    "The names of the units with investment decision must be the same for all scenarios."
                    f"For scenario {first_scenario_name} there were the units:\n"
                    f"{submodel_first_stage_variables[first_scenario_name]}.\n"
                    f"For scenario {scenario_name} there were the units:\n"
                    f"{submodel_first_stage_variables[scenario_name]}"
                )

    def __name_of_first_scenario(self):
        return next(iter(self._scenarios.names()))

    def _create_global_first_stage_variables(
        self, global_model: pyo.Model, submodel_first_stage_variables: dict[str, dict[str, pyo.Var]]
    ) -> dict[str, pyo.Var]:
        global_first_stage_variables = {}
        first_scenario_name = self.__name_of_first_scenario()
        global_model.first_stage_variables = pyo.Block()
        for var_name, _p_out_nom in submodel_first_stage_variables[first_scenario_name].items():
            var = pyo.Var(within=pyo.Reals)
            global_first_stage_variables[var_name] = var
            global_model.first_stage_variables.add_component(var_name, var)
        return global_first_stage_variables

    def _equate_global_first_stage_variables_to_submodel_first_stage_variables(
        self, scenarios_block: pyo.Block, global_first_stage_variables, submodel_first_stage_variables
    ):
        for scenario_name in self._scenarios.names():
            scenario_block: pyo.Block = getattr(scenarios_block, scenario_name)
            for var_name, p_out_nom in submodel_first_stage_variables[scenario_name].items():

                def constrain_investment_decision(m, p_out_nom=p_out_nom, var_name=var_name):
                    return p_out_nom == global_first_stage_variables[var_name]

                constraint = pyo.Constraint(rule=constrain_investment_decision)
                scenario_block.add_component(f"constrain_investment_decision_of_{var_name}", constraint)

    def root_solution(self) -> dict[str, float]:
        first_stage_result = {}
        for var_name, var in self._first_stage_variables.items():
            first_stage_result[var_name] = pyo.value(var)
        return first_stage_result
