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

import ray
import copy
import psutil
import time

from pycity_scheduling.classes import (CityDistrict, Building, Photovoltaic, WindEnergyConverter)
from pycity_scheduling.algorithms.algorithm import IterationAlgorithm, DistributedAlgorithm, SolverNode
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS
from pycity_scheduling.algorithms.algorithm_ray import RayDerivativeFreeALADINSolverNode, list_into_n_chunks


class DerivativeFreeALADINRay_Hvet(IterationAlgorithm, DistributedAlgorithm):
    """
    Implementation of the distributed ALADIN algorithm using ray.io parallelization and an improved
    implementation for sparse Hessian matrices and gradients.
    Specifically, this class implements the derivative-free ALADIN as described in [1].

    Parameters
    ----------
    city_district : CityDistrict
    solver : str, optional
        Solver to use for solving (sub)problems.
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
        Primal stopping criterion for the ALADIN algorithm.
    eps_dual : float, optional
        Dual stopping criterion for the ALADIN algorithm.
    rho : float, optional
        Penalty term parameter for the ALADIN algorithm.
    alpha : float, optional
        Step size parameter for the ALADIN algorithm.
    max_iterations : int, optional
        Maximum number of ALADIN iterations.
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    ray_cpu_count : int, optional
        Number of CPU cores to be used by ray for parallelization.
        Default: Detect the number of CPUs automatically.

    References
    ----------
    [1] "Distributed Optimization and Control with ALADIN" by Boris Houska and Yuning Jiang
    Online: https://faculty.sist.shanghaitech.edu.cn/faculty/boris/paper/AladinChapter.pdf (accessed on 2024/02/13)
    """
    def __init__(self, city_district, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS, mode="convex",
                 eps_primal=0.001, eps_dual=0.001, rho=0.5, alpha=1.0, hessian_scaling=1.0, max_iterations=10000,
                 robustness=None, ray_cpu_count=None):
        super(DerivativeFreeALADINRay_Hvet, self).__init__(city_district, solver, solver_options, mode)
        self.eps_primal = eps_primal
        self.eps_dual = eps_dual
        self.hessian_scaling = hessian_scaling
        self.rho = rho
        self.alpha = alpha
        self.max_iterations = max_iterations
        self.op_horizon = self.city_district.op_horizon

        # Only consider entities of type CityDistrict, Building, Photovoltaic, WindEnergyConverter
        self._entities = [entity for entity in self.entities if
                          isinstance(entity, (CityDistrict, Building, Photovoltaic, WindEnergyConverter))]

        # Initialize ray before using ray functions
        self.ray_cpu_count = ray_cpu_count

        # Ray initialization on a single machine vs. on an active ray cluster:
        try:
            ray.shutdown()
            if self.ray_cpu_count is not None:
                ray.init(ignore_reinit_error=True, num_cpus=int(self.ray_cpu_count))
            else:
                ray.init(ignore_reinit_error=True, num_cpus=min(len(self._entities), psutil.cpu_count(logical=False)))
        except:
            ray.init(ignore_reinit_error=True)
        resources = ray.cluster_resources()

        # Create a remote ray actor solver node for each available CPU core
        node_num = len(ray.nodes())
        if self.ray_cpu_count is not None:
            cpu_count = self.ray_cpu_count
        else:
            cpu_count = int(max(resources["CPU"], psutil.cpu_count(logical=False)))
        entity_chunks = copy.deepcopy(list(list_into_n_chunks(self._entities,
                                                              int(min(cpu_count, len(self._entities))))))
        print("{} nodes available | {} CPUs available/defined | {} entities are present | {} entity chunks created".
            format(node_num, cpu_count, len(self._entities), len(entity_chunks)))

        self.nodes = []
        self.global_entity_indices = dict()

        for i, chunk in zip(range(len(entity_chunks)), entity_chunks):
            for chunk_entity in chunk:
                # Find index of entity in self._entities and safe it to the dictionary
                global_entity_index = (
                    next((i for i, item in enumerate(self._entities) if item.id == chunk_entity.id), -1))
                self.global_entity_indices.update({chunk_entity.id: global_entity_index})
            self.nodes.append(RayDerivativeFreeALADINSolverNode.remote(solver, solver_options,
                                                                       entities=chunk,
                                                                       rho=self.rho,
                                                                       hessian_scaling=self.hessian_scaling,
                                                                       node_index=i,
                                                                       op_horizon=self.op_horizon,
                                                                       mode=mode,
                                                                       robustness=robustness))

        # Add objectives on all remotes
        add_obj_refs = [node.add_objective.remote() for node in self.nodes]

        # Wait until pyomo parameter calculation is finished on all nodes
        while len(add_obj_refs) > 0:
            done_add_obj_refs, add_obj_refs = ray.wait(add_obj_refs)
            for ref in done_add_obj_refs:
                ray.get(ref)

        # Initialize the ALADIN QP model:
        self.qp_solver = pyomo.SolverFactory(solver, **solver_options.get("__call__", {}))
        self.qp_solver_options = solver_options
        self.qp_model = pyomo.ConcreteModel()
        self.qp_model.size_t = pyomo.RangeSet(0, self.op_horizon - 1)
        self.qp_model.size_n = pyomo.RangeSet(0, len(self._entities) - 1)
        self.qp_model.size_n_t = pyomo.Set(initialize=self.qp_model.size_n * self.qp_model.size_t)
        self.qp_model.x = pyomo.Param(self.qp_model.size_n_t, mutable=True, initialize=0)
        self.qp_model.delta_x = pyomo.Var(self.qp_model.size_n_t, domain=pyomo.Reals, initialize=0)
        self.qp_model.gradient_k = pyomo.Param(self.qp_model.size_n_t, mutable=True, initialize=0)
        self.qp_model.hessian_k = pyomo.Param(self.qp_model.size_n_t, mutable=True, initialize=0)

        self._add_constraint_qp()
        self._add_objective_qp()

    def _add_objective_qp(self):
        obj = 0.0
        for i in range(len(self._entities)):
            # add Hessian part to QP objective
            for j in range(self.op_horizon):
                obj += self.qp_model.delta_x[i, j] * self.qp_model.hessian_k[i, j] * self.qp_model.delta_x[i, j]

            # add gradient part to QP objective
            for j in range(self.op_horizon):
                obj += self.qp_model.gradient_k[i, j] * self.qp_model.delta_x[i, j]
        self.qp_model.o = pyomo.Objective(expr=obj)
        self.qp_model.dual = pyomo.Suffix(direction=pyomo.Suffix.IMPORT)
        return

    def _add_constraint_qp(self):
        def qp_constraint(model, t):
            sum = 0.0
            for i in range(len(self._entities)):
                sum += model.x[i, t] + model.delta_x[i, t]
            return sum == 0.0
        self.qp_model.qp_constr = pyomo.Constraint(self.qp_model.size_t, rule=qp_constraint)
        return

    def _presolve(self, full_update, beta, robustness, debug):
        results, params = super()._presolve(full_update, beta, robustness, debug)

        set_model_beta_refs = []
        # Set the model betas on each node
        for i, node in enumerate(self.nodes):
            set_model_beta_refs.append(node.set_model_betas.remote(params))
            if full_update:
                set_model_beta_refs.append(node.full_update.remote(robustness))

        while len(set_model_beta_refs):
            done_set_model_beta_refs, set_model_beta_refs = ray.wait(set_model_beta_refs)
            for ref in done_set_model_beta_refs:
                ray.get(ref)

        results["QP_times"] = []
        
        results["r_norms"] = []
        results["s_norms"] = []

        for entity_id in self.global_entity_indices.keys():
            results[str(self.global_entity_indices[entity_id]) + "_times"] = []
        
        # initializing hessian before iterations
        params["hessian_k"] = np.zeros((len(self._entities), self.op_horizon, self.op_horizon))
        for i in range(len(self._entities)):
            params["hessian_k"][i] = self.hessian_scaling * np.eye(self.op_horizon)  # ToDo: make it adjustable

            for j in range(self.op_horizon):
                self.qp_model.hessian_k[i, j] = params["hessian_k"][i][j][j]

        return results, params

    def _postsolve(self, results, params, debug):
        # ------------------------------------------
        # 1) Remote post solve
        # ------------------------------------------
        # Execute a remote version of the postsolve method on each node,
        # the local schedules of each entity are the calculated
        ray.get([node.postsolve.remote() for node in self.nodes])

        schedule_dict = dict()
        get_schedules_refs = [node.get_all_schedules.remote() for node in self.nodes]
        # ------------------------------------------
        # 2) Wait for remote post solves
        # ------------------------------------------
        # Wait until all nodes are finished and retrieve there local dictionary
        # The dictionary contains each asset id with its corresponding schedules
        while len(get_schedules_refs) > 0:
            done_get_schedules_refs, get_schedules_refs = ray.wait(get_schedules_refs)
            for done_schedule in done_get_schedules_refs:
                node_schedules = ray.get(done_schedule)
                schedule_dict.update(node_schedules)

        # ------------------------------------------
        # 3) Local schedule update
        # ------------------------------------------
        # Update the local entities with the schedules calculated on the remote nodes
        for entity in self._entities:
            if not isinstance(entity, CityDistrict):
                for asset in entity.get_all_entities():
                    if hasattr(asset, "id"):
                        schedules = schedule_dict.get(asset.id)
                        if schedules is not None:
                            asset.schedules = schedules
            if hasattr(entity, "id"):
                schedules = schedule_dict.get(entity.id)
                if schedules is not None:
                    entity.schedules = schedules

        city_district = self._entities[0]
        for entity in city_district.get_all_entities():
            if hasattr(entity, "id"):
                schedules = schedule_dict.get(entity.id)
                if schedules is not None:
                    entity.schedules = schedules

        # Terminate all ray actors
        for node in self.nodes:
            node.exit.remote()

        if ray.is_initialized is True:
            ray.shutdown()

        # inversion of the sign of the final aggregator schedule:
        self.city_district.p_el_schedule = -self.city_district.p_el_schedule
        return

    def _is_last_iteration(self, results, params, debug):
        if super(DerivativeFreeALADINRay_Hvet, self)._is_last_iteration(results, params, debug):
            return True
        return results["r_norms"][-1] <= self.eps_primal and results["s_norms"][-1] <= self.eps_dual

    def _iteration(self, results, params, debug):
        super(DerivativeFreeALADINRay_Hvet, self)._iteration(results, params, debug)

        # fill parameters if not already present
        if "x" not in params:
            params["x"] = np.zeros((len(self._entities), self.op_horizon))
        if "delta_x" not in params:
            params["delta_x"] = np.zeros((len(self._entities), self.op_horizon))
        if "lambda_k" not in params:
            params["lambda_k"] = np.zeros(self.op_horizon)
        if "x_k" not in params:
            params["x_k"] = np.zeros((len(self._entities), self.op_horizon))
        if "gradient_k" not in params:
            params["gradient_k"] = np.zeros((len(self._entities), self.op_horizon))
        if "hessian_k" not in params:
            params["hessian_k"] = np.zeros((len(self._entities), self.op_horizon, self.op_horizon))

        # ------------------------------------------
        # 0) Storage for variables
        # ------------------------------------------
        p_el_schedules = np.zeros((len(self._entities), self.op_horizon))
        lambda_k = params["lambda_k"]
        x_k = params["x_k"]

        lambda_k_stored = ray.put(lambda_k)
        x_k_stored = ray.put(x_k)
        global_entity_indices_stored = ray.put(self.global_entity_indices)

        # ------------------------------------------
        # 1) Optimize all entities
        # ------------------------------------------
        solve_ids = [node.solve.remote(variable_refs=[lambda_k_stored, x_k_stored, global_entity_indices_stored],
                                       debug=debug) for i, node in zip(range(len(self.nodes)), self.nodes)]

        obj_value = 0
        while len(solve_ids):
            done_solve_ids, solve_ids = ray.wait(solve_ids)
            for done_solve_id in done_solve_ids:
                returns = ray.get(done_solve_id)
                obj_value += returns[2]
                for entity_id, entity_value, sub_time_val in zip(returns[0], returns[1], returns[3]):
                    global_index = self.global_entity_indices[entity_id]
                    p_el_schedules[global_index] = entity_value
                    results[str(global_index)+"_times"].append(sub_time_val)

        # extract solutions ("p_el" values) for each sub-problem
        for i in range(len(self._entities)):
            params["x"][i] = p_el_schedules[i]

        r = sum(p_el_schedules[:])
        s = np.zeros_like(params["x"])
        for i in range(len(self._entities)):
            s[i] = (params["x"][i] - params["x_k"][i])
        results["r_norms"].append(np.linalg.norm(r, 2))
        results["s_norms"].append(np.linalg.norm(s.flatten(), 2))

        # ------------------------------------------
        # 2) Solve centralized QP
        # ------------------------------------------
        t_0 = time.monotonic()
        for i in range(len(self._entities)):
            params["gradient_k"][i] = np.matmul(params["hessian_k"][i],
                                                params["x_k"][i] - params["x"][i]) - params["lambda_k"]

            for j in range(self.op_horizon):
                self.qp_model.x[i, j] = params["x"][i][j]
                self.qp_model.gradient_k[i, j] = params["gradient_k"][i][j]

        if self.solver == "gurobi_direct" or self.solver == "gurobi":
            qp_solver_options = self.qp_solver_options.get("solve", {})
            self.qp_solver.solve(self.qp_model, **qp_solver_options)
        elif self.solver == "gurobi_persistent":
            self.qp_solver.set_instance(self.qp_model)
            qp_solver_options = self.qp_solver_options.get("solve", {})
            self.qp_solver.solve(**qp_solver_options)
        else:
            raise "Gurobi solver supported only!"
        
        t_1 = time.monotonic()
        results['QP_times'].append(t_1 - t_0)

        # extract solutions ("delta_x" and "lambda_k" values) for the centralized QP
        dual_qp = -np.array([self.qp_model.dual[self.qp_model.qp_constr[t]] for t in range(self.op_horizon)])
        for i in range(len(self._entities)):
            for t in range(self.op_horizon):
                params["delta_x"][i][t] = pyomo.value(self.qp_model.delta_x[i, t])

        # ------------------------------------------
        # 3) Update of ALADIN variables
        # ------------------------------------------
        params["lambda_k"] = params["lambda_k"] + self.alpha * (dual_qp - params["lambda_k"])

        for i in range(len(self._entities)):
            for t in range(self.op_horizon):
                params["x_k"][i][t] = params["x"][i][t] + self.alpha * params["delta_x"][i][t]

        results["obj_value"].append(obj_value)
        return