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
import time


from pycity_scheduling.classes import (CityDistrict, Building, Photovoltaic, WindEnergyConverter)
from pycity_scheduling.algorithms.algorithm import IterationAlgorithm, DistributedAlgorithm, SolverNode
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS


class DerivativeFreeALADIN(IterationAlgorithm, DistributedAlgorithm):
    """
    Implementation of the distributed ALADIN algorithm.
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

    References
    ----------
    [1] "Distributed Optimization and Control with ALADIN" by Boris Houska and Yuning Jiang
    Online: https://faculty.sist.shanghaitech.edu.cn/faculty/boris/paper/AladinChapter.pdf (accessed on 2024/02/13)
    """
    def __init__(self, city_district, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS, mode="convex",
                 eps_primal=0.001, eps_dual=0.001, rho=0.5, alpha=1.0, hessian_scaling=1.0, max_iterations=10000,
                 robustness=None):
        super(DerivativeFreeALADIN, self).__init__(city_district, solver, solver_options, mode)
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

        # Create a solver node for each entity
        self.nodes = [SolverNode(solver, solver_options, [entity], mode, robustness=robustness)
                      for entity in self._entities]

        # Initialize the ALADIN QP model:
        self.qp_solver = pyomo.SolverFactory(solver, **solver_options.get("__call__", {}))
        self.qp_solver_options = solver_options
        self.qp_model = pyomo.ConcreteModel()
        self.qp_model.size_t = pyomo.RangeSet(0, self.op_horizon - 1)
        self.qp_model.size_n = pyomo.RangeSet(0, len(self._entities) - 1)
        self.qp_model.size_n_t = pyomo.Set(initialize=self.qp_model.size_n * self.qp_model.size_t)
        self.qp_model.size_n_t_t = pyomo.Set(
            initialize=self.qp_model.size_n * self.qp_model.size_t * self.qp_model.size_t)
        self.qp_model.x = pyomo.Param(self.qp_model.size_n_t, mutable=True, initialize=0)
        self.qp_model.delta_x = pyomo.Var(self.qp_model.size_n_t, domain=pyomo.Reals, initialize=0)
        self.qp_model.gradient_k = pyomo.Param(self.qp_model.size_n_t, mutable=True, initialize=0)
        self.qp_model.hessian_k = pyomo.Param(self.qp_model.size_n_t_t, mutable=True, initialize=0)

        # Create pyomo parameters for each entity
        for node, entity in zip(self.nodes, self._entities):
            node.model.beta = pyomo.Param(mutable=True, initialize=1)
            node.model.rho = pyomo.Param(mutable=True, initialize=self.rho)
            node.model.lambda_k = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            node.model.x_k = pyomo.Param(entity.model.t, mutable=True, initialize=0)
        self._add_objective()
        self._add_constraint_qp()
        self._add_objective_qp()

    def _get_objective(self):
        obj_value = 0
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            obj_value += pyomo.value(entity.get_objective())
        return obj_value

    def _add_objective(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            obj = node.model.beta * entity.get_objective()
            # ToDo: Attention - Currently only defined for "price", "co2", "peak-shaving" and "least-squares"
            decision_vars = entity.get_decision_var()

            # lambda penalty term
            for t in range(self.op_horizon):
                obj += node.model.lambda_k[t] * decision_vars[t]

            # augmented penalty term
            # ToDo: Define custom scaling...
            scaling_i = self.hessian_scaling * np.eye(self.op_horizon)
            penalty = [decision_vars[t] - node.model.x_k[t] for t in range(self.op_horizon)]
            for j in range(self.op_horizon):
                for k in range(self.op_horizon):
                    if scaling_i[j][k] != 0.0:
                        obj += node.model.rho * (penalty[j] * scaling_i[j][k] * penalty[k])
            node.model.o = pyomo.Objective(expr=obj)
        return

    def _add_objective_qp(self):
        obj = 0.0
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            # add Hessian part to QP objective
            for j in range(self.op_horizon):
                for k in range(self.op_horizon):
                    obj += self.qp_model.delta_x[i, j] * self.qp_model.hessian_k[i, j, k] * self.qp_model.delta_x[i, k]

            # add gradient part to QP objective
            for j in range(self.op_horizon):
                obj += self.qp_model.gradient_k[i, j] * self.qp_model.delta_x[i, j]
        self.qp_model.o = pyomo.Objective(expr=obj)
        self.qp_model.dual = pyomo.Suffix(direction=pyomo.Suffix.IMPORT)
        return

    def _add_constraint_qp(self):
        def qp_constraint(model, t):
            sum = 0.0
            for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                sum += model.x[i, t] + model.delta_x[i, t]
            return sum == 0.0
        self.qp_model.qp_constr = pyomo.Constraint(self.qp_model.size_t, rule=qp_constraint)
        return

    def _presolve(self, full_update, beta, robustness, debug):
        results, params = super()._presolve(full_update, beta, robustness, debug)
        for node, entity in zip(self.nodes, self._entities):
            node.model.beta = self._get_beta(params, entity)
            if full_update:
                node.full_update(robustness)
        results["QP_times"] = []

        results["r_norms"] = []
        results["s_norms"] = []

        return results, params

    def _postsolve(self, results, params, debug):
        # inversion of the sign of the final aggregator schedule:
        self.city_district.p_el_schedule = -self.city_district.p_el_schedule
        return

    def _is_last_iteration(self, results, params, debug):
        if super(DerivativeFreeALADIN, self)._is_last_iteration(results, params, debug):
            return True
        return results["r_norms"][-1] <= self.eps_primal and results["s_norms"][-1] <= self.eps_dual

    def _iteration(self, results, params, debug):
        super(DerivativeFreeALADIN, self)._iteration(results, params, debug)

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
        # 1) Solve all local problems
        # ------------------------------------------
        to_solve_nodes = []
        variables = []
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            for t in range(self.op_horizon):
                node.model.lambda_k[t] = params["lambda_k"][t]
                node.model.x_k[t] = params["x_k"][i][t]
            node.obj_update()
            to_solve_nodes.append(node)
            variables.append([entity.model.p_el_vars[t] for t in range(self.op_horizon)])
        self._solve_nodes(results, params, to_solve_nodes, variables=variables, debug=debug)

        # extract solutions ("p_el" values) for each sub-problem
        p_el_schedules = np.stack([entity.p_el_schedule for entity in self._entities], axis=0)
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            params["x"][i] = p_el_schedules[i]

        r = sum(p_el_schedules[:])
        s = np.zeros_like(params["x"])
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            s[i] = (params["x"][i] - params["x_k"][i])
        results["r_norms"].append(np.linalg.norm(r, 2))
        results["s_norms"].append(np.linalg.norm(s.flatten(), 2))

        # ------------------------------------------
        # 2) Solve centralized QP
        # ------------------------------------------
        t_0 = time.monotonic()
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            params["hessian_k"][i] = self.hessian_scaling * np.eye(self.op_horizon)  # ToDo: make it adjustable
            params["gradient_k"][i] = np.matmul(params["hessian_k"][i],
                                                params["x_k"][i] - params["x"][i]) - params["lambda_k"]

            for j in range(self.op_horizon):
                self.qp_model.x[i, j] = params["x"][i][j]
                self.qp_model.gradient_k[i, j] = params["gradient_k"][i][j]
                for k in range(self.op_horizon):
                    self.qp_model.hessian_k[i, j, k] = params["hessian_k"][i][j][k]

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
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            for t in range(self.op_horizon):
                params["delta_x"][i][t] = pyomo.value(self.qp_model.delta_x[i, t])

        # ------------------------------------------
        # 3) Update of ALADIN variables
        # ------------------------------------------
        params["lambda_k"] = params["lambda_k"] + self.alpha * (dual_qp - params["lambda_k"])

        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            for t in range(self.op_horizon):
                params["x_k"][i][t] = params["x"][i][t] + self.alpha * params["delta_x"][i][t]

        results["obj_value"].append(self._get_objective())
        return