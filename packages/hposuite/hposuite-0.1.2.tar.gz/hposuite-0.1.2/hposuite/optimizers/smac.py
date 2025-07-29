"""hposuite interface for SMAC Optimizers."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NoReturn

from ConfigSpace import ConfigurationSpace
from hpoglue import Config, Optimizer, Problem, Query
from hpoglue.budget import CostBudget, TrialBudget
from hpoglue.env import Env
from smac import (
    AlgorithmConfigurationFacade,
    BlackBoxFacade,
    HyperbandFacade,
    HyperparameterOptimizationFacade,
    MultiFidelityFacade,
    Scenario,
)
from smac.acquisition.function import (
    EI,
    EIPS,
    LCB,
    PI,
    TS,
    PriorAcquisitionFunction,
)
from smac.runhistory import StatusType, TrialValue

from hposuite.utils import set_priors_as_defaults

if TYPE_CHECKING:
    from hpoglue import Result
    from hpoglue.fidelity import Fidelity
    from smac.facade import AbstractFacade
    from smac.runhistory import TrialInfo


acq_funcs = {
    "EI": EI,
    "EIPS": EIPS,
    "LCB": LCB,
    "PI": PI,
    "TS": TS,
}


bo_facades = {
    "AlgConf": AlgorithmConfigurationFacade,
    "BlackBox": BlackBoxFacade,
    "HPO": HyperparameterOptimizationFacade,
}

def _dummy_target_function(*args: Any, budget: int | float, seed: int) -> NoReturn:  # noqa: ARG001
    raise RuntimeError("This should never be called!")


class SMAC_Optimizer(Optimizer):
    """Default SMAC Optimizer."""

    env = Env(
        name="SMAC-2.1",
        python_version="3.10",
        requirements=("smac==2.1",)
    )


    def __init__(
        self,
        *,
        problem: Problem,
        seed: int,
        working_directory: Path,
        optimizer: AbstractFacade,
        fidelity: Fidelity | None,
    ):
        """Create a SMAC Optimizer instance for a given problem.

        Args:
            problem: The problem to optimize.

            seed: Random seed for the optimizer.

            working_directory: Working directory to store SMAC run.

            config_space: Configuration space to optimize over.

            optimizer: SMAC optimizer instance.

            fidelity: Fidelity space to optimize over, if any.
        """
        self.problem = problem
        self.working_directory = working_directory
        self.optimizer = optimizer
        self.config_space = problem.config_space
        self._trial_lookup: dict[Hashable, TrialInfo] = {}
        self._fidelity = fidelity
        self._seed = seed

    def ask(self) -> Query:
        """Ask SMAC for a new config to evaluate."""
        smac_info = self.optimizer.ask()
        assert smac_info.instance is None, "We don't do instance benchmarks!"

        config = smac_info.config
        raw_config = dict(config)
        config_id = str(self.optimizer.intensifier.runhistory.config_ids[config])

        fidelity = smac_info.budget

        match fidelity:
            case None:
                fidelity = None
            case float() | int():
                assert self._fidelity is not None
                assert isinstance(self.problem.fidelities, tuple)
                fidelity_value = int(fidelity) if self._fidelity.kind is int else fidelity
                fidelity_name = self.problem.fidelities[0]
                fidelity = (fidelity_name, fidelity_value)
            case _:
                raise NotImplementedError("Unexpected return type for SMAC budget!")

        return Query(
            config=Config(config_id=config_id, values=raw_config),
            fidelity=fidelity,
            optimizer_info=smac_info,
        )

    def tell(self, result: Result) -> None:
        """Tell SMAC the result of the query."""
        match self.problem.objectives:
            case Mapping():
                cost = [
                    obj.as_minimize(result.values[key])
                    for key, obj in self.problem.objectives.items()
                ]
            case (key, obj):
                cost = obj.as_minimize(result.values[key])
            case _:
                raise TypeError("Objective must be a string or a list of strings")

        self.optimizer.tell(
            result.query.optimizer_info,  # type: ignore
            TrialValue(
                cost=cost,
                time=0.0,
                starttime=0.0,
                endtime=0.0,
                status=StatusType.SUCCESS,
                additional_info={},
            ),
            save=True,
        )


class SMAC_BO(SMAC_Optimizer):
    """SMAC Bayesian Optimization."""

    name = "SMAC_BO"

    support = Problem.Support(
        fidelities=(None,),
        objectives=("single", "many"),
        cost_awareness=(None,),
        tabular=False,
    )

    mem_req_mb = 1024

    def __init__(
        self,
        *,
        problem: Problem,
        seed: int,
        working_directory: Path,
        facade: Literal[
            "HPO",
            "BlackBox",
            "AlgConf",
        ] = "BlackBox",
        acq_func: Literal[
            "EI",
            "EIPS",
            "LCB",
            "PI",
            "TS",
        ] = "EI",
        acq_func_kwargs: dict[str, Any] | None = None,
    ):
        """Create a SMAC BO Optimizer instance for a given problem.

        Args:
            problem: The problem to optimize.

            seed: Random seed for the optimizer.

            working_directory: Working directory to store SMAC run.

            facade: The SMAC facade to use.
                - "HPO": HyperparameterOptimizationFacade
                - "BlackBox": BlackBoxFacade
                - "AlgConf": AlgorithmConfigurationFacade
            Defaults to "BlackBox".

            acq_func: The acquisition function to use.
                - "EI": Expected Improvement
                - "EIPS": Expected Improvement per Second
                - "LCB": Lower Confidence Bound
                - "PI": Probability of Improvement
                - "TS": Thompson Sampling

            acq_func_kwargs: Additional arguments for the acquisition function.
                Defaults to None.
                See SMAC documentation for details.
        """
        assert facade in bo_facades, f"Unknown facade for SMAC_BO: {facade}"
        assert acq_func in acq_funcs, f"Unknown acquisition function for SMAC_BO: {acq_func}"

        config_space = problem.config_space
        match config_space:
            case ConfigurationSpace():
                pass
            case list():
                raise ValueError("SMAC does not support tabular benchmarks!")
            case _:
                raise TypeError("Config space must be a list or a ConfigurationSpace!")

        match problem.fidelities:
            case None:
                pass
            case tuple() | Mapping():
                raise ValueError("SMAC BO does not support multi-fidelity benchmarks!")
            case _:
                raise TypeError("Fidelity must be a string or a list of strings!")

        match problem.objectives:
            case Mapping():
                metric_names = list(problem.objectives.keys())
            case (metric_name, _):
                metric_names = metric_name
            case _:
                raise TypeError("Objective must be a tuple of (name, metric) or a mapping")

        working_directory.mkdir(parents=True, exist_ok=True)

        match problem.budget:
            case TrialBudget():
                budget = problem.budget.total
            case CostBudget():
                raise ValueError("SMAC BO does not support cost-aware benchmarks!")
            case _:
                raise TypeError("Budget must be a TrialBudget or a CostBudget!")

        scenario = Scenario(
            configspace=config_space,
            deterministic=True,
            objectives=metric_names,
            n_trials=budget,
            seed=seed,
            output_directory=working_directory / "smac-output",
            min_budget=None,
            max_budget=None,
        )

        facade: AbstractFacade = bo_facades[facade]

        acquisition_func = acq_funcs[acq_func](
            **acq_func_kwargs
        )

        super().__init__(
            problem=problem,
            seed=seed,
            working_directory=working_directory,
            fidelity=None,
            optimizer=facade(
                scenario=scenario,
                logging_level=False,
                target_function=_dummy_target_function,
                intensifier=facade.get_intensifier(scenario),
                acquisition_function=acquisition_func,
                overwrite=True,
            ),
        )


class SMAC_Hyperband(SMAC_Optimizer):
    """SMAC Hyperband."""

    name = "SMAC_Hyperband"
    support = Problem.Support(
        fidelities=("single",),
        objectives=("single", "many"),
        cost_awareness=(None,),
        tabular=False,
        continuations=True,
    )
    mem_req_mb = 1024

    def __init__(  # noqa: PLR0912
        self,
        *,
        problem: Problem,
        seed: int,
        working_directory: Path,
        eta: int = 3,
    ):
        """Create a SMAC Hyperband Optimizer instance for a given problem.

        Args:
            problem: The problem to optimize.

            seed: Random seed for the optimizer.

            working_directory: Working directory to store SMAC run.

            eta: Sets the aggressiveness of Hyperband's aggressive
                early stopping by retaining 1/eta configurations every round.
                Defaults to 3.
        """
        config_space = problem.config_space
        match config_space:
            case ConfigurationSpace():
                pass
            case list():
                raise ValueError("SMAC does not support tabular benchmarks!")
            case _:
                raise TypeError("Config space must be a list or a ConfigurationSpace!")

        min_fidelity: float | int
        max_fidelity: float | int
        match problem.fidelities:
            case None:
                raise ValueError("SMAC Hyperband requires a fidelity space!")
            case Mapping():
                raise ValueError("SMAC Hyperband does not support many-fidelity!")
            case (_, fidelity):
                _fid = fidelity
                min_fidelity = fidelity.min
                max_fidelity = fidelity.max
            case _:
                raise TypeError("Fidelity must be a string or a list of strings!")

        match problem.objectives:
            case Mapping():
                metric_names = list(problem.objectives.keys())
            case (metric_name, _):
                metric_names = metric_name
            case _:
                raise TypeError("Objective must be a tuple of (name, metric) or a mapping")

        working_directory.mkdir(parents=True, exist_ok=True)
        match problem.budget:
            case TrialBudget():
                budget = problem.budget.total
            case CostBudget():
                raise ValueError("SMAC Hyperband does not support cost-aware benchmarks!")
            case _:
                raise TypeError("Budget must be a TrialBudget or a CostBudget!")

        scenario = Scenario(
            configspace=config_space,
            deterministic=True,
            objectives=metric_names,
            n_trials=budget,
            seed=seed,
            output_directory=working_directory / "smac-output",
            min_budget=min_fidelity,
            max_budget=max_fidelity,
        )
        super().__init__(
            problem=problem,
            seed=seed,
            working_directory=working_directory,
            fidelity=_fid,
            optimizer=HyperbandFacade(
                scenario=scenario,
                logging_level=False,
                target_function=_dummy_target_function,
                intensifier=HyperbandFacade.get_intensifier(scenario, eta=eta),
                overwrite=True,
            ),
        )


class SMAC_BOHB(SMAC_Optimizer):
    """SMAC BOHB."""

    name = "SMAC_BOHB"
    support = Problem.Support(
        fidelities=("single",),
        objectives=("single", "many"),
        cost_awareness=(None,),
        tabular=False,
        continuations=True,
    )
    mem_req_mb = 1024

    def __init__(  # noqa: PLR0912
        self,
        *,
        problem: Problem,
        seed: int,
        working_directory: Path,
        eta: int = 3,
    ):
        """Create a SMAC BOHB Optimizer instance for a given problem.

        Args:
            problem: The problem to optimize.

            seed: Random seed for the optimizer.

            working_directory: Working directory to store SMAC run.

            eta: Sets the aggressiveness of Hyperband's aggressive
                early stopping by retaining 1/eta configurations every round.
                Defaults to 3.
                According to the paper, changing this doesn't seem to make a difference.
        """
        config_space = problem.config_space
        match config_space:
            case ConfigurationSpace():
                pass
            case list():
                raise ValueError("SMAC does not support tabular benchmarks!")
            case _:
                raise TypeError("Config space must be a list or a ConfigurationSpace!")

        min_fidelity: float | int
        max_fidelity: float | int
        match problem.fidelities:
            case None:
                raise ValueError("SMAC BOHB requires a fidelity space!")
            case Mapping():
                raise ValueError("SMAC BOHB does not support many-fidelity!")
            case (_, fidelity):
                _fid = fidelity
                min_fidelity = fidelity.min
                max_fidelity = fidelity.max
            case _:
                raise TypeError("Fidelity must be a string or a list of strings!")

        match problem.objectives:
            case Mapping():
                metric_names = list(problem.objectives.keys())
            case (metric_name, _):
                metric_names = metric_name
            case _:
                raise TypeError("Objective must be a tuple of (name, metric) or a mapping")

        working_directory.mkdir(parents=True, exist_ok=True)
        match problem.budget:
            case TrialBudget():
                budget = problem.budget.total
            case CostBudget():
                raise ValueError("SMAC BOHB does not support cost-aware benchmarks!")
            case _:
                raise TypeError("Budget must be a TrialBudget or a CostBudget!")

        scenario = Scenario(
            configspace=config_space,
            deterministic=True,
            objectives=metric_names,
            n_trials=budget,
            seed=seed,
            output_directory=working_directory / "smac-output",
            min_budget=min_fidelity,
            max_budget=max_fidelity,
        )
        super().__init__(
            problem=problem,
            seed=seed,
            working_directory=working_directory,
            fidelity=_fid,
            optimizer=MultiFidelityFacade(
                scenario=scenario,
                logging_level=False,
                target_function=_dummy_target_function,
                intensifier=MultiFidelityFacade.get_intensifier(scenario, eta=eta),
                overwrite=True,
            ),
        )


class SMAC_PiBO(SMAC_Optimizer):
    """πBO Optimizer in SMAC."""

    name = "SMAC_PiBO"

    support = Problem.Support(
        fidelities=(None,),
        objectives=("single"),
        cost_awareness=(None,),
        tabular=False,
        priors=True,
    )

    mem_req_mb = 1024

    def __init__(  # noqa: C901, PLR0912
        self,
        *,
        problem: Problem,
        seed: int,
        working_directory: Path,
        decay_beta: float = 10.0,
        facade: Literal[
            "HPO",
            "BlackBox",
            "AlgConf",
        ] = "HPO",
        acq_func: Literal[
            "EI",
            "EIPS",
            "LCB",
            "PI",
            "TS",
        ] = "EI",
        acq_func_kwargs: dict[str, Any] | None = None,
    ):
        """Create a SMAC BO Optimizer instance for a given problem.

        Args:
            problem: The problem to optimize.

            seed: Random seed for the optimizer.

            working_directory: Working directory to store SMAC run.

            decay_beta: Parameter to control the decay of the prior strength
            in the acquisition function.

            facade: The SMAC facade to use.
                - "HPO": HyperparameterOptimizationFacade
                - "BlackBox": BlackBoxFacade
                - "AlgConf": AlgorithmConfigurationFacade
            Defaults to "HPO".

            acq_func: The acquisition function to use.
                - "EI": Expected Improvement
                - "EIPS": Expected Improvement per Second
                - "LCB": Lower Confidence Bound
                - "PI": Probability of Improvement
                - "TS": Thompson Sampling
            acq_func_kwargs: Additional arguments for the acquisition function.
                Defaults to None.
                See SMAC documentation for details.
        """
        assert facade in bo_facades, f"Unknown facade for SMAC_PiBO: {facade}"
        assert acq_func in acq_funcs, f"Unknown acquisition function for SMAC_PiBO: {acq_func}"

        config_space = problem.config_space
        match config_space:
            case ConfigurationSpace():
                pass
            case list():
                raise ValueError("SMAC does not support tabular benchmarks!")
            case _:
                raise TypeError("Config space must be a list or a ConfigurationSpace!")

        match problem.fidelities:
            case None:
                pass
            case tuple() | Mapping():
                raise ValueError("SMAC BO does not support multi-fidelity benchmarks!")
            case _:
                raise TypeError("Fidelity must be a string or a list of strings!")

        match problem.objectives:
            case Mapping():
                metric_names = list(problem.objectives.keys())
            case (metric_name, _):
                metric_names = metric_name
            case _:
                raise TypeError("Objective must be a tuple of (name, metric) or a mapping")

        working_directory.mkdir(parents=True, exist_ok=True)

        match problem.budget:
            case TrialBudget():
                budget = problem.budget.total
            case CostBudget():
                raise ValueError("SMAC BO does not support cost-aware benchmarks!")
            case _:
                raise TypeError("Budget must be a TrialBudget or a CostBudget!")

        match problem.priors:
            case None:
                raise ValueError("SMAC PiBO requires priors!")
            case tuple():
                assert len(problem.priors[1]) == 1, (
                    "SMAC PiBO doesn't support multi-objective priors! "
                )
                prior = next(iter(problem.priors[1].values()))
            case _:
                raise TypeError(
                    "Priors must be a tuple of (name, dict(objective, Config). "
                    f"Got {type(problem.priors)}"
                )

        config_space = set_priors_as_defaults(
            config_space=config_space,
            priors=prior,
        )

        scenario = Scenario(
            configspace=config_space,
            deterministic=True,
            objectives=metric_names,
            n_trials=budget,
            seed=seed,
            output_directory=working_directory / "smac-output",
            min_budget=None,
            max_budget=None,
        )

        facade: AbstractFacade = bo_facades[facade]

        acquisition_func = acq_funcs[acq_func](
            **acq_func_kwargs
        )

        super().__init__(
            problem=problem,
            seed=seed,
            working_directory=working_directory,
            fidelity=None,
            optimizer=facade(
                scenario=scenario,
                logging_level=False,
                target_function=_dummy_target_function,
                intensifier=facade.get_intensifier(scenario),
                acquisition_function=PriorAcquisitionFunction(
                    acquisition_function=acquisition_func,
                    decay_beta=scenario.n_trials / decay_beta,
                ),
                overwrite=True,
            ),
        )