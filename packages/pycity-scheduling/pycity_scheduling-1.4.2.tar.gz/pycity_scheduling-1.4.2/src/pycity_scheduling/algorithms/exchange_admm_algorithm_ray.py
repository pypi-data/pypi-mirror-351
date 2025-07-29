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

from pycity_scheduling.classes import (CityDistrict, Building, Photovoltaic, WindEnergyConverter)
# from pycity_scheduling.util import extract_pyomo_values
from pycity_scheduling.algorithms.algorithm import IterationAlgorithm, DistributedAlgorithm
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS
from pycity_scheduling.algorithms.algorithm_ray import RayADMMSolverNode, list_into_n_chunks


class ExchangeADMMRay(IterationAlgorithm, DistributedAlgorithm):
    """
    Implementation of the distributed ADMM algorithm using ray.io parallelization.
    This class implements the Exchange ADMM as described in [1].

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
        Primal stopping criterion for the ADMM algorithm.
    eps_dual : float, optional
        Dual stopping criterion for the ADMM algorithm.
    rho : float, optional
        Step size for the ADMM algorithm.
    varying_penalty_parameter : bool, optional
        Apply a varying penalty parameter scheme, see [3] - chapter 3.4.1
    tau_incr : float, optional
        Varying penalty parameter scheme increase parameter
    tau_decr : float, optional
        Varying penalty parameter scheme decrease parameter
    mu : float, optional
        Varying penalty parameter scheme conditional change parameter
    max_iterations : int, optional
        Maximum number of ADMM iterations.
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    ray_cpu_count : int, optional
        Number of CPU cores to be used by ray for parallelization.
        Default: Detect the number of CPUs automatically.

    References
    ----------
    [1] "Alternating Direction Method of Multipliers for Decentralized
    Electric Vehicle Charging Control" by Jose Rivera, Philipp Wolfrum,
    Sandra Hirche, Christoph Goebel, and Hans-Arno Jacobsen
    Online: https://mediatum.ub.tum.de/doc/1187583/1187583.pdf (accessed on 2020/09/28)

    [2] "Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers" by
    Stephen Boyd, Neal Parikh, Eric Chu, Borja Peleato, and Jonathan Eckstein
    Online: https://web.stanford.edu/~boyd/papers/pdf/admm_distr_stats.pdf (accessed on 2023/10/09)
    """
    def __init__(self, city_district, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS, mode="convex",
                 eps_primal=0.1, eps_dual=1.0, rho=2.0, max_iterations=10000, varying_penalty_parameter=False,
                 tau_incr=2.0, tau_decr=2.0, mu=10.0, robustness=None, ray_cpu_count=None):
        super(ExchangeADMMRay, self).__init__(city_district, solver, solver_options, mode)
        self.eps_primal = eps_primal
        self.eps_dual = eps_dual
        self.rho = rho
        self.varying_penalty_parameter = varying_penalty_parameter
        self.tau_incr = tau_incr
        self.tau_decr = tau_decr
        self.mu = mu
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
            self.nodes.append(RayADMMSolverNode.remote(solver, solver_options, entities=chunk, rho=self.rho,
                                                       node_index=i, op_horizon=self.op_horizon,
                                                       mode=mode, robustness=robustness))

        # Add objectives on all remotes
        add_obj_refs = [node.add_objective.remote(global_entity_indices = self.global_entity_indices)
                        for node in self.nodes]

        # Wait until pyomo parameter calculation is finished on all nodes
        while len(add_obj_refs) > 0:
            done_add_obj_refs, add_obj_refs = ray.wait(add_obj_refs)
            for ref in done_add_obj_refs:
                ray.get(ref)

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

        results["r_norms"] = []
        results["s_norms"] = []
        results["rho_value"] = []
        return results, params

    def _is_last_iteration(self, results, params, debug):
        if super(ExchangeADMMRay, self)._is_last_iteration(results, params, debug):
            return True
        return results["r_norms"][-1] <= self.eps_primal and results["s_norms"][-1] <= self.eps_dual

    def _iteration(self, results, params, debug):
        super(ExchangeADMMRay, self)._iteration(results, params, debug)

        # fill parameters if not already present
        if "p_el" not in params:
            params["p_el"] = np.zeros((len(self._entities), self.op_horizon))
        if "x_" not in params:
            params["x_"] = np.zeros(self.op_horizon)
        if "u" not in params:
            params["u"] = np.zeros(self.op_horizon)

        last_p_el = params["p_el"]
        last_x_ = params["x_"]
        last_u = params["u"]

        # ------------------------------------------
        # 0) Storage for variables
        # ------------------------------------------
        p_el_schedules_list = [None] * len(self._entities)
        last_p_el_stored = ray.put(last_p_el)
        last_x__stored = ray.put(last_x_)
        last_u_stored = ray.put(last_u)
        global_entity_indices_stored = ray.put(self.global_entity_indices)

        # ------------------------------------------
        # 1) Optimize all entities
        # ------------------------------------------
        solve_ids = [node.solve.remote(variable_refs=[last_p_el_stored, last_x__stored, last_u_stored,
                                                      global_entity_indices_stored], debug=debug)
                     for i, node in zip(range(len(self.nodes)), self.nodes)]

        obj_value = 0
        while len(solve_ids):
            done_solve_ids, solve_ids = ray.wait(solve_ids)
            for done_solve_id in done_solve_ids:
                returns = ray.get(done_solve_id) 
                obj_value += returns[2]
                for entity_id, entity_value in zip(returns[0], returns[1]):
                    global_index = self.global_entity_indices[entity_id]
                    p_el_schedules_list[global_index] = entity_value

        # ------------------------------------------
        # 2) Calculate incentive signal update
        # ------------------------------------------
        p_el_schedules = np.array(p_el_schedules_list)
        x_ = (-p_el_schedules[0] + sum(p_el_schedules[1:])) / len(self._entities)

        # ------------------------------------------
        # 3) Calculate parameters for stopping criteria
        # ------------------------------------------
        results["r_norms"].append(np.sqrt(len(self._entities)) * np.linalg.norm(x_))

        s = np.zeros_like(p_el_schedules)
        s[0] = - self.rho * (-p_el_schedules[0] + last_p_el[0] + last_x_ - x_)
        for i in range(1, len(self._entities)):
            s[i] = - self.rho * (p_el_schedules[i] - last_p_el[i] + last_x_ - x_)
        results["s_norms"].append(np.linalg.norm(s.flatten()))

        results["obj_value"].append(obj_value)

        # if desired, vary the penalty parameter
        if self.varying_penalty_parameter:
            if results["r_norms"][-1] > self.mu * results["s_norms"][-1]:
                self.rho *= float(self.tau_incr)
            elif results["s_norms"][-1] > self.mu * results["r_norms"][-1]:
                self.rho /= float(self.tau_decr)
            ray.get([node.update_rho.remote(self.rho) for node in self.nodes])
        results["rho_value"].append(self.rho)

        # ------------------------------------------
        # 4) Save required parameters for another iteration
        # ------------------------------------------
        params["p_el"] = p_el_schedules
        params["x_"] = x_
        params["u"] += x_
        return

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
        return
