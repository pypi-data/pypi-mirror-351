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
import matplotlib.pyplot as plt

import ray
import copy
import psutil

from pycity_scheduling.classes import (CityDistrict, Building, Photovoltaic, WindEnergyConverter)
from pycity_scheduling.algorithms.algorithm import IterationAlgorithm, DistributedAlgorithm
from pycity_scheduling.algorithms.algorithm_ray import RayADMMMIQPSolverNode, list_into_n_chunks
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS


class ExchangeMIQPADMMRay(IterationAlgorithm, DistributedAlgorithm):
    """Implementation of the Exchange MIQP ADMM algorithm.

    Implements the Exchange MIQP ADMM algorithm described in [1], [2], and [3] using parallel computations with Ray.

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
    eps_exch_primal : float, optional
        Primal stopping criterion for the ADMM algorithm.
    eps_exch_dual : float, optional
        Dual stopping criterion for the ADMM algorithm.
    gamma : float, optional
        Exchange MIQP ADMM scaling parameter
    gamma_incr : float, optional
        Varying scaling parameter scheme increase parameter
    rho : float, optional
        Stepsize for the ADMM algorithm.
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

    [2] "A simple effective heuristic for embedded mixed-integer quadratic programming" by Reza Takapoui,
    Nicholas Moehle, Stephen Boyd, and Alberto Bemporad
    Online: https://web.stanford.edu/~boyd/papers/pdf/miqp_admm.pdf (accessed on 2023/09/06)

    [3] "Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers" by
    Stephen Boyd, Neal Parikh, Eric Chu, Borja Peleato, and Jonathan Eckstein
    Online: https://web.stanford.edu/~boyd/papers/pdf/admm_distr_stats.pdf (accessed on 2023/10/09)
    """
    def __init__(self, city_district, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS,
                 mode="convex", x_update_mode="constrained", eps_exch_primal=0.01, eps_exch_dual=0.1, gamma=1.0,
                 gamma_incr=1.0, rho=2.0, varying_penalty_parameter=False, tau_incr=2.0, tau_decr=2.0, mu=10.0,
                 max_iterations=10000, robustness=None, ray_cpu_count=None):
        super(ExchangeMIQPADMMRay, self).__init__(city_district, solver, solver_options, mode)

        self.x_update_mode = x_update_mode
        self.eps_exch_primal = eps_exch_primal
        self.eps_exch_dual = eps_exch_dual
        self.gamma = gamma
        self.gamma_incr = gamma_incr
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
            self.nodes.append(RayADMMMIQPSolverNode.remote(solver, 
                                                           solver_options, 
                                                           entities=chunk,
                                                           gamma=self.gamma,
                                                           rho=self.rho,
                                                           node_index=i,
                                                           max_iterations=self.max_iterations, 
                                                           op_horizon=self.op_horizon, 
                                                           mode=mode,
                                                           x_update_mode=self.x_update_mode, 
                                                           robustness=robustness))

        # Additions to the Exchange ADMM algorithm in order to obtain Exchange MIQP ADMM
        self.feasible = False

        # Set parameters on all remotes
        set_param_refs = [node.set_model_parameters.remote() for node in self.nodes]

        # Wait until set parameters is finished on all nodes
        while len(set_param_refs) > 0:
            done_set_param_refs, set_param_refs = ray.wait(set_param_refs)
            for ref in done_set_param_refs:
                ray.get(ref)
        
        self._add_objective(exchange_admm_obj_terms=True, miqp_admm_obj_terms=True)

    # Returns True, if no constraint or binary variable violations occur
    def _check_violations(self, print_out=True, detailed_print_out=False):
        constr_counter = 0
        var_counter = 0
        number_constraints = 0
        number_binaries = 0
        # Get parameters from all remote nodes
        get_counter_refs = [node.check_violations.remote(detailed_print_out=detailed_print_out) for node in self.nodes]
        # Wait until get parameters is finished on all nodes
        while len(get_counter_refs):
            done_get_counter_refs, get_counter_refs = ray.wait(get_counter_refs)
            for done_get_counter_ref in done_get_counter_refs:
                returns = ray.get(done_get_counter_ref)
                constr_counter += returns[0]
                var_counter  += returns[1]
                number_constraints += returns[2]
                number_binaries  += returns[3]

        if print_out:
            print("Violated constraints:", constr_counter,  "of in total", number_constraints)
            print("Violated binaries:", var_counter, "of in total", number_binaries)
        if var_counter == 0 and constr_counter == 0:
            return True
        else:
            return False

    # Returns the objective value
    def _get_objective(self):
        # Get parameters from all remote nodes
        get_obj_refs = [node.get_objective.remote() for node in self.nodes]
        obj_value = 0
        # Wait until get parameters is finished on all nodes
        while len(get_obj_refs) > 0:
            done_get_obj_refs, get_obj_refs = ray.wait(get_obj_refs)
            for ref in done_get_obj_refs:
                remote_obj_value = ray.get(ref)
                obj_value += remote_obj_value
        return obj_value

    def _add_objective(self, exchange_admm_obj_terms=True, miqp_admm_obj_terms=True):
        # Add objective on all remotes
        add_obj_refs = [node.add_objective.remote(exchange_admm_obj_terms, miqp_admm_obj_terms) for node in self.nodes]
        # Wait until objectives have been set on all nodes
        while len(add_obj_refs) > 0:
            done_add_obj_refs, add_obj_refs = ray.wait(add_obj_refs)
            for ref in done_add_obj_refs:
                returned = ray.get(ref)
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

        results["r_norms"] = []
        results["s_norms"] = []
        results["gamma_value"] = []
        results["rho_value"] = []
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
        # Wait until all nodes are finished and retrive there local dictionary
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
        return

    def _is_last_iteration(self, results, params, debug):
        if super(ExchangeMIQPADMMRay, self)._is_last_iteration(results, params, debug):
            self._check_violations()
            return True
        if results["r_norms"][-1] <= self.eps_exch_primal and results["s_norms"][-1] <= self.eps_exch_dual:
            if self.feasible:
                self._check_violations()
                return True
            else:
                return False

    def _iteration(self, results, params, debug):
        super(ExchangeMIQPADMMRay, self)._iteration(results, params, debug)
        op_horizon = self._entities[0].op_horizon

        # fill parameters if not already present
        if "p_el" not in params:
            params["p_el"] = np.zeros((len(self._entities), op_horizon))
        if "x_" not in params:
            params["x_"] = np.zeros(op_horizon)
        if "u" not in params:
            params["u"] = np.zeros(op_horizon)
        last_u = params["u"]
        last_p_el = params["p_el"]
        last_x_ = params["x_"]

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
                                                      global_entity_indices_stored], update_constr=True, debug=debug)
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
        results["r_norms"].append(np.sqrt(len(self._entities)) * np.linalg.norm(x_))

        s = np.zeros_like(p_el_schedules)
        s[0] = - self.rho * (-p_el_schedules[0] + last_p_el[0] + last_x_ - x_)
        for i in range(1, len(self._entities)):
            s[i] = - self.rho * (p_el_schedules[i] - last_p_el[i] + last_x_ - x_)
        results["s_norms"].append(np.linalg.norm(s.flatten()))

        results["obj_value"].append(self._get_objective())

        # To check the latest solution for feasibility, fix all binary vars at either 0 or 1 and try to recalculate the
        # schedule based on an additional optimization. Of course, there are other and possibly more
        # straightforward ways to check for feasibility. This will be future work.
        if ((results["r_norms"][-1] <= self.eps_exch_primal) and (results["s_norms"][-1] <= self.eps_exch_dual)) or \
                (results["iterations"][-1] >= self.max_iterations):
            if results["iterations"][-1] >= self.max_iterations:
                print("Iteration " + str(results["iterations"][-1]) + ": " +
                      "Maximum iteration limit reached. Checking the current solution for feasibility.")
            else:
                print("Iteration " + str(results["iterations"][-1]) + ": " +
                      "Stopping criteria satisfied. Checking the current solution for feasibility.")
            self._add_objective(exchange_admm_obj_terms=True, miqp_admm_obj_terms=True)
            self.fix_variables()
            if self.x_update_mode == "unconstrained":
                self.activate_constraints()

            solve_ids = [node.solve.remote(variable_refs=[last_p_el_stored, last_x__stored, last_u_stored,
                                                          global_entity_indices_stored], update_constr=True,
                                           debug=False) for i, node in zip(range(len(self.nodes)), self.nodes)]
            self.feasible = True
            while len(solve_ids):
                done_solve_ids, solve_ids = ray.wait(solve_ids)
                for done_solve_id in done_solve_ids:
                    returns = ray.get(done_solve_id) 
                    self.feasible = self.feasible and returns[3]

            if self.feasible:
                print("Success. The solution is feasible!")
                self.release_variables()
                if self.x_update_mode == "unconstrained":
                    self.deactivate_constraints()
            else:
                print("Failure. The solution is infeasible, because at least one subsystem is (still) infeasible!")
                if results["iterations"][-1] >= self.max_iterations:
                    print("Attention: The final solution could be infeasible!")
                else:
                    self._add_objective(exchange_admm_obj_terms=True, miqp_admm_obj_terms=True)
                    self.release_variables()
                    if self.x_update_mode == "unconstrained":
                        self.deactivate_constraints()
                    solve_ids = [node.solve.remote(variable_refs=[last_p_el_stored, last_x__stored, last_u_stored,
                                                                  global_entity_indices_stored], update_constr=True,
                                                   debug=False) for i, node in zip(range(len(self.nodes)), self.nodes)]
                    while len(solve_ids):
                        done_solve_ids, solve_ids = ray.wait(solve_ids)
                        for done_solve_id in done_solve_ids:
                            returns = ray.get(done_solve_id)
                # vary the gamma parameter (maximum value is 10e9 to avoid numerical issues):
                self.gamma = min(float(self.gamma_incr)*self.gamma, 10e9)
                ray.get([node.update_gamma.remote(self.gamma) for node in self.nodes])
        results["gamma_value"].append(self.gamma)

        # ----------------------------------------
        # 3) incentive signal update (MIQP ADMM)
        # ----------------------------------------
        incentive_refs = [node.incentive_signal_update.remote(results["iterations"][-1]-1) for node in self.nodes]

        while len(incentive_refs) > 0:
            done_incentive_refs, incentive_refs = ray.wait(incentive_refs)
            for ref in done_incentive_refs:
                result = ray.get(ref)

        # if desired, vary the penalty parameter
        if self.varying_penalty_parameter:
            if results["r_norms"][-1] > self.mu * results["s_norms"][-1]:
                self.rho *= float(self.tau_incr)
            elif results["s_norms"][-1] > self.mu * results["r_norms"][-1]:
                self.rho /= float(self.tau_decr)
            ray.get([node.update_rho.remote(self.rho) for node in self.nodes])
        results["rho_value"].append(self.rho)

        # save parameters for another iteration
        params["p_el"] = p_el_schedules
        params["x_"] = x_
        params["u"] += x_
        return

    def fix_variables(self):
        fix_vars_refs = [node.fix_variables.remote() for node in self.nodes]
        while len(fix_vars_refs) > 0:
            done_fix_vars_refs, fix_vars_refs = ray.wait(fix_vars_refs)
            for ref in done_fix_vars_refs:
                ray.get(ref)
        return

    def release_variables(self):
        release_vars_refs = [node.release_variables.remote() for node in self.nodes]
        while len(release_vars_refs) > 0:
            done_release_vars_refs, release_vars_refs = ray.wait(release_vars_refs)
            for ref in done_release_vars_refs:
                ray.get(ref)
        return

    def activate_constraints(self):
        # Set parameters on all remotes
        activate_contraints_refs = [node.activate_constraints.remote() for node in self.nodes]

        # Wait until set parameters is finished on all nodes
        while len(activate_contraints_refs) > 0:
            done_activate_contraints_refs, activate_contraints_refs = ray.wait(activate_contraints_refs)
            for ref in done_activate_contraints_refs:
                ray.get(ref)
        return

    def deactivate_constraints(self):
        # Set parameters on all remotes
        deactivate_contraints_refs = [node.deactivate_constraints.remote() for node in self.nodes]

        # Wait until set parameters is finished on all nodes
        while len(deactivate_contraints_refs) > 0:
            done_deactivate_contraints_refs, deactivate_contraints_refs = ray.wait(deactivate_contraints_refs)
            for ref in done_deactivate_contraints_refs:
                ray.get(ref)
        return
