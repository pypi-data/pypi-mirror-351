"""
The pycity_scheduling framework


Copyright (C) 2025,
Institute for Automation of Complex Power Systems (ACS),
E.ON Energy Research Center (E.ON ERC),
RWTH Aachen University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import numpy as np
import time
import logging
import warnings
import pyomo.environ as pyomo
from pyomo.solvers.plugins.solvers.persistent_solver import PersistentSolver
from pyomo.opt import SolverStatus, TerminationCondition

from pycity_scheduling.classes import CityDistrict, Building, ElectricalGrid
from pycity_scheduling.exceptions import NonoptimalError
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS


class OptimizationAlgorithm:
    """
    Base class for all optimization algorithms.

    This class provides functionality common to all algorithms which are
    able to optimize City Districts.

    Parameters
    ----------
    city_district : CityDistrict
    solver : str, optional
        Solver to use for solving (sub-)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance`,
        `solve`.

        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory. In addition to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.

    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear, i.e., convex, constraints
        - `integer` : May use non-linear, i.e., mixed-integer, constraints
    """

    def __init__(self, city_district, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS, mode="convex"):
        self.city_district = city_district
        self.entities = [city_district]
        self.entities.extend([node["entity"] for node in city_district.nodes.values()])
        if self.city_district.electrical_grid is not None:
            self.entities.append(self.city_district.electrical_grid)
        self.solver = solver
        self.solver_options = solver_options
        self.mode = mode
        self._reset()

    def _add_objective(self):
        """Adds the modified objective of the entities to their specific models."""
        raise NotImplementedError("This method should be implemented by subclass.")

    def solve(self, full_update=True, beta=1, robustness=None, debug=False):
        """Solves the city district for the current op_horizon.

        Parameters
        ----------
        full_update : bool, optional
            Should be true if the city district models were changed or
            update_model should be called to update the city district models.
            Disabling the full_update can give a small performance gain.
        beta : float, optional
            Tradeoff factor between system and customer objective. The customer
            objective is multiplied with beta.
        robustness : tuple, optional
            Tuple of two floats. First entry defines how many time steps are
            protected from deviations. Second entry defines the magnitude of
            deviations which are considered.
        debug : bool, optional
            Specify whether detailed debug information shall be printed.

        Returns
        -------
        results : dict
            Dictionary of performance values of the algorithm.

        Raises
        ------
        NonoptimalError
            If no feasible solution for the city district is found or a solver
            problem is encountered.
        """
        results, params = self._presolve(full_update, beta, robustness, debug)
        params["start_time"] = time.monotonic()
        self._solve(results, params, debug)
        self._postsolve(results, params, debug)
        return results

    def _save_time(self, results, params):
        """Saves the current runtime into results."""
        results["times"].append(time.monotonic() - params["start_time"])
        return

    @staticmethod
    def _get_beta(params, entity):
        """Returns the beta value for a specific entity."""
        beta = params["beta"]
        if isinstance(beta, dict):
            return beta.get(entity.id, 1.0)
        if isinstance(entity, CityDistrict):
            return 1.0
        return beta

    def _reset(self):
        """Reset, i.e., 'unpopulate', the previous optimization model."""
        city_district = self.entities[0]
        city_district.model = None
        for bd in city_district.get_lower_entities():
            bd.model = None
            if isinstance(bd, Building) and bd.has_bes:
                bd.bes.model = None
                for e in bd.bes.get_lower_entities():
                    e.model = None
            if isinstance(bd, Building) and len(bd.apartments) == 1:
                bd.apartments[0].model = None
                for e in bd.apartments[0].get_lower_entities():
                    e.model = None
            elif isinstance(bd, Building) and len(bd.apartments) > 1:
                for ap in bd.apartments:
                    ap.model = None
                    for e in ap.get_lower_entities():
                        e.model = None

    def _presolve(self, full_update, beta, robustness, debug):
        """Step before the optimization of (sub-)problems.

        Parameters
        ----------
        full_update : bool
            Should be true if the city district models were changed or
            update_model should be called to update the city district models.
            Disabling the full_update can give a small performance gain.
        beta : float
            Tradeoff factor between system and customer objective. The customer
            objective is multiplied with beta.
        robustness : tuple, optional
            Tuple of two floats. First entry defines how many time steps are
            protected from deviations. Second entry defines the magnitude of
            deviations which are considered.
        debug : bool, optional
            Specify whether detailed debug information shall be printed.

        Returns
        -------
        results : dict
            Dictionary in which performance values of the algorithm can be stored.
        params : dict
            Dictionary in which the algorithm can store intermediate results for
            later access in the algorithm itself. This dictionary should contain
            all which is generated and used by the algorithm.
        """
        params = {"beta": beta, "robustness": robustness}
        results = {"times": []}
        return results, params

    def _solve(self, results, params, debug):
        """Step in which (sub-)problems are optimized.

        Parameters
        ----------
        results : dict
            Dictionary in which performance values of the algorithm are stored.
        params : dict
            Dictionary in which intermediate results are stored.
        debug : bool
            Specify whether detailed debug information shall be printed.
        """
        raise NotImplementedError("This method should be implemented by the subclass.")

    def _postsolve(self, results, params, debug):
        """Step after optimization.

        In this step other post-processing can be done.

        Parameters
        ----------
        results : dict
            Dictionary in which performance values of the algorithm are stored.
        params : dict
            Dictionary in which intermediate results are stored.
        debug : bool
            Specify whether detailed debug information shall be printed.
        """
        return


class IterationAlgorithm(OptimizationAlgorithm):
    """Base class for all optimization algorithms that solve the problem iteratively."""
    def _solve(self, results, params, debug):
        if "iterations" not in results:
            results["iterations"] = []
        if "obj_value" not in results:
            results["obj_value"] = []
        iterations = results["iterations"]
        is_last_iteration = False
        while not is_last_iteration:
            iterations.append((iterations[-1] + 1) if len(iterations) > 0 else 1)
            self._iteration(results, params, debug=debug)
            self._save_time(results, params)
            is_last_iteration = self._is_last_iteration(results, params, debug)
        return

    def _iteration(self, results, params, debug):
        """Execute a single iteration of the algorithm.

        Parameters
        ----------
        results : dict
            Dictionary in which performance values of the algorithm are stored.
        params : dict
            Dictionary in which intermediate results are stored.
        """
        return

    def _is_last_iteration(self, results, params, debug):
        """Returns True if the current iteration is the last one.
            It checks if the iteration limit is exceeded.
            Overwrite this function to apply additional, individual stopping criteria other than the iteration limit.
            Anyway, this parent method must be called in a child method, so that the check of an exceeded iteration
            limit below is executed.

        Parameters
        ----------
        debug : bool, optional
            Specify whether detailed debug information shall be printed.
        Raises
        ------
        Warning
            If the stopping criteria can not be reached in max_iterations.
        NonoptimalError
            If no feasible solution for the city district is found or a solver
            problem is encountered.
        """
        if results["iterations"][-1] >= self.max_iterations:
            if debug:
                warnings.warn("User defined iteration limit exceeded")
            print("Exceeded the user defined iteration limit of {0} iterations. "
                  "Terminating the iterative algorithm.".format(self.max_iterations))
            return True
        return False


class DistributedAlgorithm(OptimizationAlgorithm):
    """Base class for all distributed optimization algorithms.

    These algorithms can divide the optimization problem into sub-problems.
    """
    def _solve_nodes(self, results, params, nodes, variables=None, debug=True):
        """Used to indicate which nodes can be solved independently.

        Provides the "distributed_times" as a performance value to results.

        Parameters
        ----------
        results : dict
            Dictionary in which performance values of the algorithm are stored.
        params : dict
            Dictionary in which intermediate results are stored.
        nodes : list of SolverNode
            List of nodes which can be solved independently.
        variables : list of lists of variables, optional
            Can contain a list for each node in nodes to indicate to pyomo which
            variables should be loaded back into the model. Specifying this can
            lead to a significant speedup.
        debug : bool, optional
            Specify whether detailed debug information shall be printed. Defaults
            to true.
        """
        if "distributed_times" not in results:
            results["distributed_times"] = []
        if variables is None:
            variables = [None] * len(nodes)
        node_times = {}
        for node, variables_ in zip(nodes, variables):

            for entity in node.entities:
                if (str(entity.id)+"_times") not in results:
                    results[str(entity.id)+"_times"] = []

            start = time.monotonic()
            node.solve(debug=debug)
            stop = time.monotonic()

            entity_ids = tuple(entity.id for entity in node.entities)
            node_times[entity_ids] = stop - start
            for entity in node.entities:
                results[str(entity.id)+"_times"].append(stop - start)
        results["distributed_times"].append(node_times)
        return


class SolverNode:
    """Node which can be used to solve all entities provided to it.

    Provides an abstraction layer for algorithms, so entities can be
    assigned to nodes and optimized easily.

    Parameters
    ----------
    solver : str
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.

        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory.  Additionally to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.
    entities : list
        List of entities which should be optimized by this node.
    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    """
    def __init__(self, solver, solver_options, entities, mode="convex", robustness=None):
        logging.getLogger('pyomo.core').setLevel(logging.ERROR)
        self.solver = pyomo.SolverFactory(solver, node_ids=[entity.id for entity in entities],
                                          **solver_options.get("__call__", {}))
        self.solver_options = solver_options
        self.is_persistent = isinstance(self.solver, PersistentSolver)
        self.robustness = robustness
        self.entities = entities
        self.mode = mode
        self.model = None
        self._prepare()

    def _prepare(self):
        """Create the pyomo model for the entities and populate it."""
        model = pyomo.ConcreteModel()
        for entity in self.entities:
            self._prepare_model(entity, model, robustness=self.robustness)
        self.model = model
        return

    def _prepare_model(self, entity, model, robustness=None):
        """Add a single entity to a model."""
        if isinstance(entity, Building):
            entity.populate_model(model, self.mode, robustness=robustness)
            entity.update_model(self.mode, robustness=robustness)
        else:
            entity.populate_model(model, self.mode)
            entity.update_model(self.mode)
        return

    def full_update(self, robustness=None):
        """Execute the update_model function and propagate other model changes.

        Parameters
        ----------
        robustness : tuple, optional
            Tuple of two floats. First entry defines how many time steps are
            protected from deviations. Second entry defines the magnitude of
            deviations which are considered.
        """
        for entity in self.entities:
            if isinstance(entity, Building):
                entity.update_model(mode=self.mode, robustness=robustness)
            else:
                entity.update_model(mode=self.mode)
        if self.is_persistent:
            self.solver.set_instance(self.model, **self.solver_options.get("set_instance", {}))
        return

    def constr_update(self):
        """Only propagate the constraints update of the model."""
        if self.is_persistent:
            self.solver.set_instance(self.model, **self.solver_options.get("set_instance", {}))
        else:
            pass
        return

    def obj_update(self):
        """Only propagate the objective value update of the model."""
        if self.is_persistent:
            self.solver.set_objective(self.model.o)
        else:
            pass
        return

    def solve(self, debug=True):
        """Call the solver to solve this nodes optimization problem.

        Parameters
        ----------
        debug : bool, optional
            Specify whether detailed debug information shall be printed. Defaults
            to true.
        """
        solve_options = self.solver_options.get("solve", {})
        if self.is_persistent:
            result = self.solver.solve(**solve_options)
        else:
            result = self.solver.solve(self.model, **solve_options)
        if (not (result.solver.termination_condition == TerminationCondition.optimal or
                result.solver.termination_condition == TerminationCondition.maxTimeLimit or
                result.solver.termination_condition == TerminationCondition.maxIterations) or
                not (result.solver.status == SolverStatus.ok or
                     result.solver.status == SolverStatus.warning or
                     result.solver.status == SolverStatus.aborted)):
            if debug:
                import pycity_scheduling.util.debug as debug
                debug.analyze_model(self.model, self.solver, result)
            raise NonoptimalError("Could not retrieve schedule from model.")
        for entity in self.entities:
            if not isinstance(entity, ElectricalGrid):
                entity.update_schedule()
        return
