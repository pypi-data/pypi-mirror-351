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
import pyomo.environ as pyomo

from pycity_scheduling.classes import (CityDistrict, Building, Photovoltaic, WindEnergyConverter)
from pycity_scheduling.algorithms.algorithm import IterationAlgorithm, DistributedAlgorithm, SolverNode
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS


class DualDecompositionMPI(IterationAlgorithm, DistributedAlgorithm):
    """
    Implementation of the distributed Dual Decomposition algorithm as described in [1] using parallel computations with
    MPI.

    Parameters
    ----------
    city_district : CityDistrict
    mpi_interface : MPIInterface
        MPI Interface to use for solving the Dual Decomposition subproblems in parallel.
    solver : str, optional
        Solver to use for solving the (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        `__call__` is the function being called when generating an instance
        with the pyomo SolverFactory. In addition to the options provided,
        `node_ids` is passed to this call containing the IDs of the entities
        being optimized.
        `set_instance` is called when a pyomo Model is set as an instance of
        a persistent solver. `solve` is called to perform an optimization. If
        not set, `save_results` and `load_solutions` may be set to false to
        provide a speedup.
    mode : str, optional
        Specifies which set of constraints to use.
        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    eps_primal : float, optional
        Primal stopping criterion for the dual decomposition algorithm.
    rho : float, optional
        Step size for the dual decomposition algorithm.
    max_iterations : int, optional
        Maximum number of dual decomposition iterations.
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.

    References
    ----------
    [1] "Distributed Optimization for Scheduling Electrical Demand in Complex City Districts" by
    M. Diekerhof, S. Schwarz, F. Martin, A. Monti in IEEE Systems Journal, vol. 12, no. 4, pp. 3226-3237, Dec. 2018.
    """
    def __init__(self, city_district, mpi_interface, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS,
                 mode="convex", eps_primal=0.1, rho=2.0, max_iterations=10000, robustness=None):
        super(DualDecompositionMPI, self).__init__(city_district, solver, solver_options, mode)

        self.mpi_interface = mpi_interface

        self.eps_primal = eps_primal
        self.rho = rho
        self.max_iterations = max_iterations
        self.op_horizon = self.city_district.op_horizon

        # Only consider entities of type CityDistrict, Building, Photovoltaic, WindEnergyConverter
        self._entities = [entity for entity in self.entities if
                          isinstance(entity, (CityDistrict, Building, Photovoltaic, WindEnergyConverter))]

        # Create a solver node for each entity
        self.nodes = [SolverNode(solver, solver_options, [entity], mode, robustness=robustness)
                      for entity in self._entities]

        # Determine which MPI processes is responsible for which node(s):
        self.mpi_process_range = self.mpi_interface.get_mpi_process_range(len(self._entities))

        # Create pyomo parameters for each entity
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                node.model.beta = pyomo.Param(mutable=True, initialize=1)
                node.model.lambdas = pyomo.Param(entity.model.t, mutable=True, initialize=0)
        self._add_objective()

    def _add_objective(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                obj = node.model.beta * entity.get_objective()
                if i == 0:
                    # penalty term is expanded and constant is omitted
                    # invert sign of p_el_schedule and p_el_vars (omitted for quadratic term)
                    for t in range(self.op_horizon):
                        obj -= node.model.lambdas[t] * entity.model.p_el_vars[t]
                else:
                    for t in range(self.op_horizon):
                        obj += node.model.lambdas[t] * entity.model.p_el_vars[t]
                node.model.o = pyomo.Objective(expr=obj)
        return

    def _get_objective(self):
        if self.mpi_interface.mpi_size > 1:
            obj_value_list = np.zeros(len(self._entities), dtype=np.float64)
            for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                    obj_value_list[i] += pyomo.value(entity.get_objective())
            tmp = np.zeros(len(self._entities), dtype=np.float64)
            self.mpi_interface.get_comm().Allreduce(obj_value_list, tmp, self.mpi_interface.mpi.SUM)
            obj_value_list = tmp
            obj_value = np.sum(obj_value_list)
        else:
            obj_value = 0
            for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                obj_value += pyomo.value(entity.get_objective())
        return obj_value

    def _presolve(self, full_update, beta, robustness, debug):
        results, params = super()._presolve(full_update, beta, robustness, debug)
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                node.model.beta = self._get_beta(params, entity)
                if full_update:
                    node.full_update(robustness)
        results["r_norms"] = []
        results["lambdas"] = []
        return results, params

    def _postsolve(self, results, params, debug):
        if self.mpi_interface.get_size() > 1:
            # Update all models across all MPI instances:
            pyomo_var_values = dict()
            asset_updates = np.empty(len(self._entities), dtype=np.object_)
            for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                    for asset in entity.get_all_entities():
                        for v in asset.model.component_data_objects(ctype=pyomo.Var, descend_into=True):
                            pyomo_var_values[str(v)] = pyomo.value(v)
                    asset_updates[i] = pyomo_var_values

            if self.mpi_interface.get_rank() == 0:
                buffer = np.array([bytearray(10**6) for i in range(1, len(self._entities))])
                for i in range(1, len(self._entities)):
                    req = self.mpi_interface.get_comm().irecv(
                        buffer[i-1],
                        source=self.mpi_process_range[i],
                        tag=(int(results["iterations"][-1])+1) * len(self._entities) + i
                    )
                    asset_updates[i] = req.wait()
            else:
                for i in range(1, len(self._entities)):
                    if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                        req = self.mpi_interface.get_comm().isend(
                            asset_updates[i],
                            dest=0,
                            tag=(int(results["iterations"][-1])+1) * len(self._entities) + i
                        )
                        req.wait()
                asset_updates = np.empty(len(self._entities), dtype=np.object_)
            asset_updates = self.mpi_interface.get_comm().bcast(asset_updates, root=0)

            for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                for asset in entity.get_all_entities():
                    pyomo_var_values_map = pyomo.ComponentMap()
                    for v in asset.model.component_data_objects(ctype=pyomo.Var, descend_into=True):
                        if str(v) in asset_updates[i]:
                            pyomo_var_values_map[v] = pyomo.value(asset_updates[i][str(v)])
                    for var in pyomo_var_values_map:
                        var.set_value(pyomo_var_values_map[var], skip_validation=True)
                    asset.update_schedule()
        else:
            super()._postsolve(results, params, debug)
        return

    def _is_last_iteration(self, results, params, debug):
        if super(DualDecompositionMPI, self)._is_last_iteration(results, params, debug):
            return True
        return results["r_norms"][-1] <= self.eps_primal

    def _iteration(self, results, params, debug):
        super(DualDecompositionMPI, self)._iteration(results, params, debug)
        if "lambdas" not in params:
            params["lambdas"] = np.zeros(self.op_horizon)
        lambdas = params["lambdas"]

        # ------------------------------------------
        # 1) Optimize all entities
        # ------------------------------------------
        to_solve_nodes = []
        variables = []

        p_el_schedules = np.empty((len(self._entities), self.op_horizon))
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if self.mpi_interface.get_rank() == self.mpi_process_range[i]:
                for t in range(self.op_horizon):
                    node.model.lambdas[t] = lambdas[t]
                node.obj_update()
                to_solve_nodes.append(node)
                variables.append([entity.model.p_el_vars[t] for t in range(self.op_horizon)])
        self._solve_nodes(results, params, to_solve_nodes, variables=variables, debug=debug)

        if self.mpi_interface.get_rank() == 0:
            p_el_schedules[0] = np.stack(self.city_district.p_el_schedule, axis=0)
        for j in range(1, len(self._entities)):
            if self.mpi_interface.get_rank() == 0:
                if self.mpi_interface.get_size() > 1:
                    data = np.empty(self.op_horizon, dtype=np.float64)
                    req = self.mpi_interface.get_comm().Irecv(
                        data,
                        source=self.mpi_process_range[j],
                        tag=int(results["iterations"][-1]) * len(self._entities) + j
                    )
                    req.wait()
                    p_el_schedules[j] = np.array(data, dtype=np.float64)
                else:
                    p_el_schedules[j] = np.stack(self._entities[j].p_el_schedule, axis=0)
            else:
                if self.mpi_interface.get_rank() == self.mpi_process_range[j]:
                    p_el_schedules[j] = np.stack(self._entities[j].p_el_schedule, axis=0)
                    if self.mpi_interface.get_size() > 1:
                        req = self.mpi_interface.get_comm().Isend(
                            p_el_schedules[j],
                            dest=0,
                            tag=int(results["iterations"][-1]) * len(self._entities) + j
                        )
                        req.wait()

        # ------------------------------------------
        # 2) Calculate incentive signal update
        # ------------------------------------------
        if self.mpi_interface.get_rank() == 0:
            lambdas -= self.rho * p_el_schedules[0]
            lambdas += self.rho * np.sum(p_el_schedules[1:], axis=0)
            r = np.zeros(self.op_horizon)
            r -= p_el_schedules[0]
            r += np.sum(p_el_schedules[1:], axis=0)
        else:
            lambdas = np.empty(self.op_horizon, dtype=np.float64)
            r = np.empty(self.op_horizon, dtype=np.float64)
        if self.mpi_interface.get_size() > 1:
            self.mpi_interface.get_comm().Bcast(lambdas, root=0)
            self.mpi_interface.get_comm().Bcast(r, root=0)

        # ------------------------------------------
        # 3) Calculate parameters for stopping criteria
        # ------------------------------------------
        results["r_norms"].append(np.linalg.norm(r, np.inf))
        results["lambdas"].append(np.copy(lambdas))
        results["obj_value"].append(self._get_objective())

        # ------------------------------------------
        # 4) Save required parameters for another iteration
        # ------------------------------------------
        params["lambdas"] = lambdas
        return
