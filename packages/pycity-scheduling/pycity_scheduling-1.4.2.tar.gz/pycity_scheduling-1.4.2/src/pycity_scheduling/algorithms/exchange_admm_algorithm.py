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


class ExchangeADMM(IterationAlgorithm, DistributedAlgorithm):
    """
    Implementation of the distributed ADMM algorithm.
    This class implements the Exchange ADMM as described in [1] and [2].

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
                 eps_primal=0.1, eps_dual=1.0, rho=2.0, varying_penalty_parameter=False, tau_incr=2.0, tau_decr=2.0,
                 mu=10.0, max_iterations=10000, robustness=None):
        super(ExchangeADMM, self).__init__(city_district, solver, solver_options, mode)
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

        # Create a solver node for each entity
        self.nodes = [SolverNode(solver, solver_options, [entity], mode, robustness=robustness)
                      for entity in self._entities]

        # Create pyomo parameters for each entity
        for node, entity in zip(self.nodes, self._entities):
            node.model.beta = pyomo.Param(mutable=True, initialize=1)
            node.model.rho_ = pyomo.Param(mutable=True, initialize=self.rho)
            node.model.xs_ = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            node.model.us = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            node.model.last_p_el_schedules = pyomo.Param(entity.model.t, mutable=True, initialize=0)
        self._add_objective()

    def _add_objective(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            obj = node.model.beta * entity.get_objective()
            for t in range(self.op_horizon):
                obj += node.model.rho_ / 2 * entity.model.p_el_vars[t] * entity.model.p_el_vars[t]
            # penalty term is expanded and constant is omitted
            if i == 0:
                # invert sign of p_el_schedule and p_el_vars (omitted for quadratic term)
                penalty = [(-node.model.last_p_el_schedules[t] - node.model.xs_[t] - node.model.us[t])
                           for t in range(self.op_horizon)]
                for t in range(self.op_horizon):
                    obj += node.model.rho_ * penalty[t] * entity.model.p_el_vars[t]
            else:
                penalty = [(-node.model.last_p_el_schedules[t] + node.model.xs_[t] + node.model.us[t])
                           for t in range(self.op_horizon)]
                for t in range(self.op_horizon):
                    obj += node.model.rho_ * penalty[t] * entity.model.p_el_vars[t]
            node.model.o = pyomo.Objective(expr=obj)
        return

    def _get_objective(self):
        obj_value = 0
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            obj_value += pyomo.value(entity.get_objective())
        return obj_value

    def _presolve(self, full_update, beta, robustness, debug):
        results, params = super()._presolve(full_update, beta, robustness, debug)
        for node, entity in zip(self.nodes, self._entities):
            node.model.beta = self._get_beta(params, entity)
            if full_update:
                node.full_update(robustness)
        results["r_norms"] = []
        results["s_norms"] = []
        results["rho_value"] = []
        return results, params

    def _is_last_iteration(self, results, params, debug):
        if super(ExchangeADMM, self)._is_last_iteration(results, params, debug):
            return True
        return results["r_norms"][-1] <= self.eps_primal and results["s_norms"][-1] <= self.eps_dual

    def _iteration(self, results, params, debug):
        super(ExchangeADMM, self)._iteration(results, params, debug)

        # fill parameters if not already present
        if "p_el" not in params:
            params["p_el"] = np.zeros((len(self._entities), self.op_horizon))
        if "x_" not in params:
            params["x_"] = np.zeros(self.op_horizon)
        if "u" not in params:
            params["u"] = np.zeros(self.op_horizon)
        last_u = params["u"]
        last_p_el = params["p_el"]
        last_x_ = params["x_"]

        # ------------------------------------------
        # 1) Optimize all entities
        # ------------------------------------------
        to_solve_nodes = []
        variables = []
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            for t in range(self.op_horizon):
                node.model.last_p_el_schedules[t] = last_p_el[i][t]
                node.model.xs_[t] = last_x_[t]
                node.model.us[t] = last_u[t]
            node.obj_update()
            to_solve_nodes.append(node)
            variables.append([entity.model.p_el_vars[t] for t in range(self.op_horizon)])
        self._solve_nodes(results, params, to_solve_nodes, variables=variables, debug=debug)

        # ------------------------------------------
        # 2) Calculate incentive signal update
        # ------------------------------------------
        p_el_schedules = np.stack([entity.p_el_schedule for entity in self._entities], axis=0)
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

        results["obj_value"].append(self._get_objective())

        # if desired, vary the penalty parameter
        if self.varying_penalty_parameter:
            if results["r_norms"][-1] > self.mu * results["s_norms"][-1]:
                self.rho *= float(self.tau_incr)
                for node, entity in zip(self.nodes, self._entities):
                    node.model.rho_ = self.rho
            elif results["s_norms"][-1] > self.mu * results["r_norms"][-1]:
                self.rho /= float(self.tau_decr)
                for node, entity in zip(self.nodes, self._entities):
                    node.model.rho_ = self.rho
        results["rho_value"].append(self.rho)

        # ------------------------------------------
        # 4) Save required parameters for another iteration
        # ------------------------------------------
        params["p_el"] = p_el_schedules
        params["x_"] = x_
        params["u"] += x_
        return
